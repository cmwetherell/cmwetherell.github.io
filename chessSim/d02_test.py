"""
Test harness for the D.02 team-pairing engine: run a candidate pairing on the
real results of rounds 1..R-1 and score it against the official round-R pairings
from chess-results. Iterate the engine until the match rate is high.

    from d02_test import load_context, score
    ctx = load_context('open', 2)          # pair R2 from real R1
    pairs = my_pairing(ctx)                # set of frozenset({team_id_a, team_id_b})
    print(score(pairs, ctx))
"""

import pandas as pd
from collections import defaultdict

from olympiadConfig import get_event


def _gp_to_mp(gp):
    return 2 if gp > 2 else (1 if gp == 2 else 0)


def load_context(event_key, rd):
    """
    Pairing context for round `rd`, built from real results of rounds < rd.
    All team references are team_id (chess-results snr). Fields:
      teams        : list of participating team_ids
      mp           : {team_id: match points before round rd}
      gp           : {team_id: game points (board points) before rd}
      init_rank    : {team_id: starting rank}  (== team_id here)
      prev         : set of frozenset({a,b}) matchups already played
      colors       : {team_id: net board-1 color, +1 per White, -1 per Black}
      last_color   : {team_id: +1/-1 board-1 color in the previous round, 0 if none}
      official     : set of frozenset({a,b}) official pairings for round rd (ground truth)
      float_hist   : {team_id: set of rounds the team was downfloated}  (not yet populated)
    """
    cfg = get_event(event_key)
    teams_df = pd.read_csv(cfg.teams_csv)
    tid = {t: int(r) for t, r in zip(teams_df.team, teams_df.initRank)}

    rr = pd.read_csv(cfg.round_results_csv)
    prior = rr[(rr["round"] < rd) & (rr["status"] == "final")]

    mp = defaultdict(int); gp = defaultdict(float)
    colors = defaultdict(int); last_color = {}
    prev = set()
    teams = set()
    for m in prior.sort_values("round").itertuples(index=False):
        a, b = tid.get(m.team1), tid.get(m.team2)
        if a is None or b is None:
            continue
        teams.add(a); teams.add(b)
        ga = (m.team1_score_hp or 0) / 2.0
        gb = (m.team2_score_hp or 0) / 2.0
        mp[a] += _gp_to_mp(ga); mp[b] += _gp_to_mp(gb)
        gp[a] += ga; gp[b] += gb
        prev.add(frozenset((a, b)))
        # chess-results lists team1 first == board-1 White
        colors[a] += 1; colors[b] -= 1
        last_color[a] = 1; last_color[b] = -1

    teams = sorted(teams)
    off = rr[rr["round"] == rd]
    official = {frozenset((tid[x.team1], tid[x.team2])) for x in off.itertuples(index=False)
                if x.team1 in tid and x.team2 in tid}

    return {
        "event": event_key, "round": rd, "teams": teams,
        "mp": {t: mp[t] for t in teams}, "gp": {t: gp[t] for t in teams},
        "init_rank": {t: t for t in teams},
        "prev": prev, "colors": {t: colors[t] for t in teams},
        "last_color": {t: last_color.get(t, 0) for t in teams},
        "official": official, "tid": tid,
        "id2name": {v: k for k, v in tid.items()},
    }


def score(pairs, ctx, verbose=True):
    """Compare candidate `pairs` (set of frozensets) to ctx['official']."""
    off = ctx["official"]
    off_teams = set().union(*off) if off else set()
    ours_teams = set().union(*pairs) if pairs else set()
    common = {p for p in off if p <= (off_teams & set(ctx["teams"]))}
    matched = pairs & off
    mp = ctx["mp"]
    # per-scoregroup breakdown
    by_grp_tot = defaultdict(int); by_grp_mat = defaultdict(int)
    for p in off:
        a, b = tuple(p)
        key = f"{min(mp.get(a,-9), mp.get(b,-9))}-{max(mp.get(a,-9), mp.get(b,-9))}"
        by_grp_tot[key] += 1
        if p in pairs:
            by_grp_mat[key] += 1
    result = {
        "event": ctx["event"], "round": ctx["round"],
        "official": len(off), "ours": len(pairs), "matched": len(matched),
        "pct": round(100 * len(matched) / max(len(off), 1), 1),
        "by_group": {k: f"{by_grp_mat[k]}/{by_grp_tot[k]}" for k in sorted(by_grp_tot, reverse=True)},
    }
    if verbose:
        print(f"{ctx['event']} R{ctx['round']}: {result['matched']}/{result['official']} "
              f"= {result['pct']}%  by scoregroup: {result['by_group']}")
    return result


def missed_pairs(pairs, ctx, limit=15):
    """Official pairings we failed to produce, with MP/rank context."""
    mp, ir, n = ctx["mp"], ctx["init_rank"], ctx["id2name"]
    out = []
    for p in sorted(ctx["official"] - pairs, key=lambda p: -max(mp.get(t, 0) for t in p)):
        a, b = tuple(p)
        out.append(f"{n.get(a)}(mp{mp.get(a)},r{ir.get(a)}) vs {n.get(b)}(mp{mp.get(b)},r{ir.get(b)})")
    return out[:limit]
