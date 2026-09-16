"""
Validate our D.02 pairing engine against chess-results' official pairings.

For a target round R (default: the first round whose official pairings are live
but which we haven't "seen" the results-driven pairing for), we:
  1. take the actual results of rounds 1..R-1 (from chess-results, authoritative),
  2. run OUR pairing engine to generate round R,
  3. compare our matchups (who plays whom, unordered) to the official round-R
     pairings from chess-results.

Pairing (who-plays-whom) is deterministic given prior results + starting ranks,
so a correct D.02 implementation should match the official pairing. Colours are
not compared (secondary allocation).

    python chessSim/validatePairing.py open           # auto: first live future round
    python chessSim/validatePairing.py open --round 2
    python chessSim/validatePairing.py open --source lichess   # preview using Lichess R1

Exit code 0 = compared (see report); 2 = target round's official pairings not
live yet (use this to gate an auto-trigger).
"""

import sys
import argparse

import pandas as pd

from olympiadConfig import get_event
import scrapeOlympiad as scr
import olympiadResults as results
from simOlympiad import load_event, _pair_round, _gp_to_mp


def _pairset(pairs):
    """Set of unordered {a,b} frozensets."""
    return {frozenset((a, b)) for a, b in pairs}


def official_round(cfg, rd):
    """Official pairings for round rd as unordered team-name pairs, or None."""
    rr = pd.read_csv(cfg.round_results_csv)
    grp = rr[rr["round"] == rd]
    if grp.empty:
        return None
    return _pairset(zip(grp["team1"], grp["team2"]))


def _seed_from_chessresults(cfg, upto_round):
    """mp / prev / participants / init_rank from chess-results results of rounds < upto_round."""
    state = load_event(cfg)   # seeds all completed rounds from matches.csv
    # load_event seeds every completed round; restrict to < upto_round if needed.
    matches = pd.read_csv(cfg.matches_csv)
    matches = matches[matches["round"] < upto_round]
    participants = state["participants"]
    mp = {t: 0 for t in participants}
    prev = set()
    for r in matches.itertuples(index=False):
        if r.playerTeam in mp and r.oppTeam in mp:
            mp[r.playerTeam] += _gp_to_mp(r.gp)
            prev.add((r.playerTeam, r.oppTeam))
    return participants, mp, prev, state["init_rank"]


def _seed_from_lichess(cfg, upto_round):
    """Same, but reconstruct rounds < upto_round from Lichess board games."""
    state = load_event(cfg)
    participants = state["participants"]
    id2name = {v: k for k, v in state["team_id"].items()}
    mp = {t: 0 for t in participants}
    prev = set()
    for rd in range(1, upto_round):
        gdf = results.collect_round_games(cfg, rd)
        if gdf is None or gdf.empty:
            continue
        # team game points per match
        score = {}   # board_no -> {team_id: points}
        for g in gdf.itertuples(index=False):
            res = {"1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
                   "1/2-1/2": (0.5, 0.5)}.get(g.result, (0.0, 0.0))
            d = score.setdefault(g.board_no, {})
            d[g.white_team_id] = d.get(g.white_team_id, 0) + res[0]
            d[g.black_team_id] = d.get(g.black_team_id, 0) + res[1]
        for bno, d in score.items():
            tids = [t for t in d if t is not None]
            if len(tids) != 2:
                continue
            a, b = tids
            na, nb = id2name.get(a), id2name.get(b)
            if na in mp and nb in mp:
                mp[na] += _gp_to_mp(d[a]); mp[nb] += _gp_to_mp(d[b])
                prev.add((na, nb)); prev.add((nb, na))
    return participants, mp, prev, state["init_rank"]


def our_round(participants, mp, prev, init_rank):
    """Our engine's pairing for the next round given standings, as unordered pairs."""
    teams_by_rank = sorted(participants, key=lambda t: (-mp[t], init_rank[t]))
    if len(teams_by_rank) % 2:
        teams_by_rank = teams_by_rank[:-1]   # lowest-ranked gets the bye
    return _pairset(_pair_round(teams_by_rank, mp, prev))


def validate(event_key, rd=None, source="chess-results"):
    cfg = get_event(event_key)
    scr.scrape_rounds(cfg)
    rr = pd.read_csv(cfg.round_results_csv)
    if rr.empty:
        print(f"{cfg.label}: no rounds published yet"); return 2

    if rd is None:
        # first round with pairings whose PRIOR round is final (i.e. a real pairing test)
        rd = None
        for r in sorted(rr["round"].unique()):
            prior = rr[rr["round"] == r - 1]
            if r >= 2 and not prior.empty and (prior["status"] == "final").all():
                if (rr[rr["round"] == r]).shape[0] > 0:
                    rd = int(r)
        if rd is None:
            print(f"{cfg.label}: no future round with a completed prior round yet "
                  f"(R1 not final / R2 not paired). Nothing to validate."); return 2

    official = official_round(cfg, rd)
    if official is None:
        print(f"{cfg.label}: official round {rd} pairings not live yet"); return 2

    prior = rr[rr["round"] == rd - 1]
    if source == "chess-results" and not (not prior.empty and (prior["status"] == "final").all()):
        print(f"{cfg.label}: round {rd-1} not final on chess-results; "
              f"try --source lichess for a preview"); return 2

    if source == "lichess":
        participants, mp, prev, init_rank = _seed_from_lichess(cfg, rd)
    else:
        participants, mp, prev, init_rank = _seed_from_chessresults(cfg, rd)

    ours = our_round(participants, mp, prev, init_rank)

    match = ours & official
    only_ours = ours - official
    only_off = official - ours
    pct = 100 * len(match) / len(official) if official else 0
    print(f"\n===== {cfg.label}: Round {rd} pairing validation (source={source}) =====")
    print(f"official matches: {len(official)} | our matches: {len(ours)} | "
          f"identical: {len(match)} ({pct:.1f}%)")

    if only_ours or only_off:
        print(f"\n{len(only_off)} official pairings we did NOT produce:")
        for m in list(only_off)[:20]:
            a, b = tuple(m)
            print(f"  {a} (mp{mp.get(a,'?')}) vs {b} (mp{mp.get(b,'?')})")
        print(f"\n{len(only_ours)} pairings we produced that aren't official:")
        for m in list(only_ours)[:20]:
            a, b = tuple(m)
            print(f"  {a} (mp{mp.get(a,'?')}) vs {b} (mp{mp.get(b,'?')})")
    else:
        print("PERFECT MATCH — our pairing == official.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event", help="open | women")
    ap.add_argument("--round", type=int, default=None)
    ap.add_argument("--source", choices=["chess-results", "lichess"], default="chess-results")
    args = ap.parse_args()
    code = validate(args.event, args.round, args.source)
    sys.exit(code)


if __name__ == "__main__":
    main()
