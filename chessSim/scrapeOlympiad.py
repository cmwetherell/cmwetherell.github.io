"""
Scrape Olympiad data (players, teams, round results, official R1 pairings)
from chess-results.com into per-event CSVs.

One pipeline for both events -- pick the event on the command line:

    python chessSim/scrapeOlympiad.py open
    python chessSim/scrapeOlympiad.py women

Tables are located by *content*, not by a hardcoded index, because
chess-results shifts the number/order of layout tables between events
(in 2026 the player table moved from index 4 to 6, which silently broke
the old positional scraper). See olympiadConfig.py for event definitions.
"""

import os
import sys
import json
from io import StringIO

import requests
import pandas as pd

# Suppress the InsecureRequestWarning from verify=False (chess-results TLS).
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

try:
    from olympiadConfig import get_event, EventConfig, BYE, BYE_GP
except ImportError:  # when run as chessSim.scrapeOlympiad
    from chessSim.olympiadConfig import get_event, EventConfig, BYE, BYE_GP

HEADERS = {"User-agent": "Mozilla/5.0"}


def fetch_tables(url: str) -> list:
    """Return all HTML tables on a chess-results page as DataFrames."""
    resp = requests.get(url, verify=False, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return pd.read_html(StringIO(resp.text))


def _flat_text(df: pd.DataFrame) -> str:
    """Lower-cased concatenation of a table's cells + column labels."""
    parts = [str(c) for c in df.columns]
    parts += [str(v) for v in df.to_numpy().ravel()[:400]]
    return " ".join(parts).lower()


def pick_table(tables: list, must_contain, min_rows: int = 5) -> pd.DataFrame:
    """
    Return the first (largest) table whose content contains all the given
    marker strings. Prefers larger tables so we grab the data grid, not a
    small header/nav table that happens to share a word.
    """
    markers = [m.lower() for m in must_contain]
    candidates = [
        t for t in tables
        if t.shape[0] >= min_rows and all(m in _flat_text(t) for m in markers)
    ]
    if not candidates:
        raise RuntimeError(
            f"No table matching {must_contain} found "
            f"(saw {[t.shape for t in tables]})"
        )
    return max(candidates, key=lambda t: t.shape[0])


def _promote_header(df: pd.DataFrame, marker: str) -> pd.DataFrame:
    """
    Find the row containing `marker`, use it as the column header, and return
    the rows below it. Handles chess-results tables that carry a banner row
    (e.g. "Round 1 on ...") above the real header.
    """
    marker = marker.lower()
    header_idx = None
    for i in range(min(3, df.shape[0])):
        if marker in " ".join(str(v) for v in df.iloc[i]).lower():
            header_idx = i
            break
    if header_idx is None:
        return df
    out = df.copy()
    out.columns = out.iloc[header_idx]
    out = out.iloc[header_idx + 1:].reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------

def scrape_players(cfg: EventConfig) -> pd.DataFrame:
    tables = fetch_tables(cfg.url(art=16, flag=30, zeilen=99999))
    raw = pick_table(tables, ["Rtg", "Team", "Name"], min_rows=10)
    players = _promote_header(raw, "Name")

    # The player-title column has a blank header on chess-results. Detect it by
    # content (values are chess titles) and name it before dropping other blanks.
    titles = {"GM", "IM", "FM", "CM", "NM", "WGM", "WIM", "WFM", "WCM"}
    for col in players.columns:
        if pd.isna(col):
            vals = players[col].dropna().astype(str).str.strip()
            if len(vals) and (vals.isin(titles).mean() > 0.3):
                players = players.rename(columns={col: "Title"})
                break

    # Drop remaining unnamed spacer columns.
    players = players.loc[:, [c for c in players.columns if pd.notna(c)]]
    players = players.loc[:, ~players.columns.duplicated()]

    if "rtg+/-" not in players.columns:
        players["rtg+/-"] = 0
    players["rtg+/-"] = pd.to_numeric(players["rtg+/-"], errors="coerce").fillna(0)

    players["Rtg"] = pd.to_numeric(players["Rtg"], errors="coerce").fillna(0).astype(int)
    players["dR"] = players["rtg+/-"].astype(int) / 10
    if "Rp" in players.columns:
        rp = pd.to_numeric(players["Rp"], errors="coerce").fillna(0).astype(int)
        players.loc[players.Rtg == 0, "Rtg"] = rp
    players.loc[players.Rtg == 0, "Rtg"] = 1200  # unrated fallback
    players.Rtg = round(players.Rtg + players["dR"]).astype(int)

    players["Team"] = players["Team"].astype(str).str.replace(r"\s*\*\)$", "", regex=True).str.strip()

    # Keep board order as listed (Bo. ascending) so roster iloc[0..3] == boards 1-4.
    if "Bo." in players.columns:
        players["Bo."] = pd.to_numeric(players["Bo."], errors="coerce")
        players = players.sort_values(["Team", "Bo."], kind="stable")

    # Ensure every team has >= 4 players (duplicate the lowest-rated if short).
    frames = []
    for team, grp in players.groupby("Team", sort=False):
        grp = grp.copy()
        while grp.shape[0] < 4:
            grp = pd.concat([grp, grp.sort_values("Rtg").head(1)], ignore_index=True)
            print(f"  padded roster for {team} -> {grp.shape[0]} players")
        frames.append(grp)
    players = pd.concat(frames, ignore_index=True)

    os.makedirs(cfg.data_dir, exist_ok=True)
    players.to_csv(cfg.players_csv, index=False)

    team_map = players[["FED", "Team"]].drop_duplicates().set_index("Team")["FED"].to_dict()
    with open(cfg.team_map_json, "w") as fh:
        json.dump(team_map, fh)

    print(f"players: {players.shape[0]} rows, {players.Team.nunique()} teams -> {cfg.players_csv}")
    return players


# ---------------------------------------------------------------------------
# Teams (starting rank)
# ---------------------------------------------------------------------------

def scrape_teams(cfg: EventConfig) -> pd.DataFrame:
    tables = fetch_tables(cfg.url(art=32, turdet="YES", flag=30, zeilen=99999, transfer="J"))
    raw = pick_table(tables, ["Team", "RtgAvg"], min_rows=10)

    teams = pd.DataFrame({
        "initRank": pd.to_numeric(raw["No."], errors="coerce"),
        "team": raw["Team"].astype(str).str.replace(r"\s*\*\)$", "", regex=True).str.strip(),
        "fed": raw.get("FED", "").astype(str).str.strip(),
        "avg_rating": pd.to_numeric(raw.get("RtgAvg"), errors="coerce"),
        "captain": raw.get("Captain", "").astype(str).str.strip(),
    })
    teams = teams.dropna(subset=["initRank"])
    teams["initRank"] = teams["initRank"].astype(int)
    teams["avg_rating"] = teams["avg_rating"].fillna(0).astype(int)
    teams = teams.sort_values("initRank").reset_index(drop=True)

    os.makedirs(cfg.data_dir, exist_ok=True)
    teams.to_csv(cfg.teams_csv, index=False)
    print(f"teams: {teams.shape[0]} rows -> {cfg.teams_csv}")
    return teams


# ---------------------------------------------------------------------------
# Round results / official pairings
# ---------------------------------------------------------------------------

def _clean_gp(val):
    """Parse a chess-results game-point cell ('2½' -> 2.5, blank -> NaN)."""
    if pd.isna(val):
        return None
    s = str(val).strip().replace("½", ".5")
    if s in ("", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


_NON_TEAM = {"not paired", "bye", "spielfrei", "", "nan", "spielfrei / not paired"}
# A pairing-allocated bye (odd field: the lowest-ranked unpaired team). Scores
# 1 MP + 2 GP (FIDE Olympiad Regs 4.1/4.3; verified on the chess-results ranking
# table: bye teams carry +1 MP / +2 GP over their played games). Distinct from
# "not paired" = absent/withdrawn that round, which scores nothing.
_BYE = {"bye", "spielfrei"}


def _strip_team(name) -> str:
    return str(name).replace("*)", "").strip()


def _is_real_team(name: str) -> bool:
    return bool(name) and name.lower() not in _NON_TEAM


def _is_bye(name: str) -> bool:
    return str(name).strip().lower() in _BYE


def scrape_rounds(cfg: EventConfig):
    """
    Walk every round page. For each round, capture team-vs-team pairings and
    (where present) the team game points. Returns (matches_df, round1_pairings_df).

      matches_df       : completed matches (playerTeam, oppTeam, round, gp) -- both
                         perspectives per match. Empty pre-tournament.
      round1_pairings  : official R1 pairings (whiteTeam, blackTeam) -- team listed
                         first on chess-results has board-1 white.
    """
    all_matches = []     # completed team matches (sim input): playerTeam, oppTeam, round, gp
    r1_pairs = []        # official R1 pairings: whiteTeam, blackTeam
    round_results = []   # every published match (DB): round, board_no, team1, team2,
                         #   team1_score_hp, team2_score_hp, status

    for rd in range(1, cfg.n_rounds + 1):
        try:
            tables = fetch_tables(cfg.url(art=2, rd=rd, flag=30))
            grid = pick_table(tables, ["Res."], min_rows=3)
        except RuntimeError:
            # No pairing table for this round yet -> stop, nothing further published.
            break

        grid = _promote_header(grid, "Res.")
        # Positional layout of the results grid (verified against 2026 pages):
        #   0=No.(board_no)  1=SNo1  4=Team1  7=Res1  9=Res2  12=Team2  15=SNo2
        board_no = pd.to_numeric(grid.iloc[:, 0], errors="coerce")
        team1 = grid.iloc[:, 4].map(_strip_team)
        team2 = grid.iloc[:, 12].map(_strip_team)
        res1 = grid.iloc[:, 7].map(_clean_gp)
        res2 = grid.iloc[:, 9].map(_clean_gp)

        played_any = res1.notna().any()

        for bno, t1, t2, g1, g2 in zip(board_no, team1, team2, res1, res2):
            # "X vs bye": pairing-allocated bye. Record it as a match against
            # BYE so the team is seeded with its 1 MP + 2 GP and is known to be
            # active this round (a team absent from a round's pairings without a
            # bye is "not paired" -- absent/withdrawn -- and scores nothing).
            if _is_real_team(t1) and _is_bye(t2) or _is_real_team(t2) and _is_bye(t1):
                team = t1 if _is_real_team(t1) else t2
                # The bye's points count once the round is underway; for a
                # merely published future round it stays 'scheduled' (and out
                # of matches.csv, so next_round doesn't advance past it) -- the
                # sim credits it when that pinned round is played.
                round_results.append({
                    "round": rd, "board_no": int(bno) if pd.notna(bno) else None,
                    "team1": team, "team2": BYE,
                    "team1_score_hp": int(BYE_GP * 2) if played_any else None,
                    "team2_score_hp": None,
                    "status": "final" if played_any else "scheduled",
                })
                if played_any:
                    all_matches.append({"playerTeam": team, "oppTeam": BYE,
                                        "round": rd, "gp": BYE_GP})
                continue
            # Rows like "Angola vs not paired" are absent/withdrawn teams, not a
            # pairing-allocated bye -- skip them (those teams don't play).
            if not (_is_real_team(t1) and _is_real_team(t2)):
                continue
            final = g1 is not None and g2 is not None
            round_results.append({
                "round": rd,
                "board_no": int(bno) if pd.notna(bno) else None,
                "team1": t1, "team2": t2,
                "team1_score_hp": int(round(g1 * 2)) if final else None,
                "team2_score_hp": int(round(g2 * 2)) if final else None,
                "status": "final" if final else "scheduled",
            })
            if rd == 1:
                r1_pairs.append({"whiteTeam": t1, "blackTeam": t2})
            if final:
                all_matches.append({"playerTeam": t1, "oppTeam": t2, "round": rd, "gp": g1})
                all_matches.append({"playerTeam": t2, "oppTeam": t1, "round": rd, "gp": g2})

        if not played_any and rd > 1:
            # Round rd has pairings but no results (future round). We already
            # recorded its scheduled pairings above; stop walking further rounds.
            break

    matches_df = pd.DataFrame(all_matches, columns=["playerTeam", "oppTeam", "round", "gp"])
    r1_df = pd.DataFrame(r1_pairs, columns=["whiteTeam", "blackTeam"])
    results_df = pd.DataFrame(round_results, columns=[
        "round", "board_no", "team1", "team2",
        "team1_score_hp", "team2_score_hp", "status"])

    os.makedirs(cfg.data_dir, exist_ok=True)
    matches_df.to_csv(cfg.matches_csv, index=False)
    r1_df.to_csv(cfg.round1_pairings_csv, index=False)
    results_df.to_csv(cfg.round_results_csv, index=False)

    completed = int(matches_df["round"].max()) if not matches_df.empty else 0
    participants = sorted(set(r1_df.whiteTeam) | set(r1_df.blackTeam))
    print(f"rounds: {completed} completed round(s); {len(r1_df)} real R1 pairings; "
          f"{len(participants)} participating teams -> {cfg.matches_csv}")
    return matches_df, r1_df, results_df


def _gp_to_mp(gp):
    return 2 if gp > 2 else (1 if gp == 2 else 0)


def scrape_standings(cfg: EventConfig) -> pd.DataFrame:
    """
    Official team standings after EVERY completed round, from the chess-results
    ranking table (art=0&rd=N -- the rd parameter is honoured, so past rounds
    are exact, not reconstructed). Columns: after_round, team_id, rank, mp,
    gp_hp, tb1, tb2, tb3.

      rank   : official chess-results rank ("Rk.")
      mp     : match points -- DERIVED from matches.csv, cross-checked against
               the official TB1 (a mismatch is printed loudly: it means the sim
               input disagrees with chess-results)
      gp_hp  : game points in half-points -- DERIVED, cross-checked vs TB3*2
      tb1    : official TB2 = Olympiad-Sonneborn-Berger without lowest result
               (Chennai) -- the first tiebreak after match points
      tb2    : official TB3 = game points (== gp_hp / 2)
      tb3    : official TB4 = Olympiad-Sum of Adjusted matchpoints without
               lowest result (Chennai)
      (official TB1 == mp, so it is not stored twice)

    mp/gp_hp stay derived so they agree exactly with a site-side derivation
    from `matches`; rank/tb* are authoritative. If the ranking page for a round
    can't be fetched or parsed, that round falls back to the derived ranking
    (rank by mp, gp_hp; tb* null), so an update never fails on it.

    Each round's block is exactly the official page's team set: a team that
    chess-results lists but that had no match yet (a late arrival, seeded 0 MP /
    0 GP and ranked among the other 0-point teams) is included with its official
    rank, so ranks run 1..n with no gaps. Teams keyed by a superseded SNo are
    dropped when the block is written (see olympiadDB.upsert_standings).
    """
    matches = pd.read_csv(cfg.matches_csv)
    teams = pd.read_csv(cfg.teams_csv)
    team_id = {t: int(r) for t, r in zip(teams.team, teams.initRank)}

    cols = ["after_round", "team_id", "rank", "mp", "gp_hp", "tb1", "tb2", "tb3"]
    if matches.empty:
        df = pd.DataFrame(columns=cols)
        df.to_csv(cfg.standings_csv, index=False)
        print("standings: 0 completed rounds -> empty")
        return df

    completed = int(matches["round"].max())
    frames = []
    for rd in range(1, completed + 1):
        upto = matches[matches["round"] <= rd]
        agg = upto.groupby("playerTeam").agg(
            mp=("gp", lambda s: int(sum(_gp_to_mp(g) for g in s))),
            gp_hp=("gp", lambda s: int(round(s.sum() * 2))),
        ).reset_index()
        agg["team_id"] = agg.playerTeam.map(team_id)
        agg = agg.dropna(subset=["team_id"])
        agg["team_id"] = agg.team_id.astype(int)

        official = _official_ranking(cfg, rd)
        if official is None:
            agg = agg.sort_values(["mp", "gp_hp"], ascending=False).reset_index(drop=True)
            agg["rank"] = agg.index + 1
            agg["tb1"] = agg["tb2"] = agg["tb3"] = None
            print(f"standings: R{rd} official ranking unavailable -> derived rank, no tiebreaks")
        else:
            # Late arrivals are on the official page with 0 points before their
            # first pairing; give them a derived 0/0 row so the block is exact.
            known = set(team_id.values())
            unknown = official[~official.team_id.isin(known)]
            if len(unknown):
                print(f"standings: R{rd} WARNING {len(unknown)} official SNo(s) not in teams.csv "
                      f"(dropped): {unknown.team_id.tolist()[:5]}")
                official = official[official.team_id.isin(known)]
            idle = sorted(set(official.team_id) - set(agg.team_id))
            if idle:
                name_of = {v: k for k, v in team_id.items()}
                agg = pd.concat([agg, pd.DataFrame({"playerTeam": [name_of[t] for t in idle],
                                                    "mp": 0, "gp_hp": 0, "team_id": idle})],
                                ignore_index=True)
                print(f"standings: R{rd} {len(idle)} team(s) on official ranking without a match yet "
                      f"(0/0): {[name_of[t] for t in idle][:5]}")
            agg = agg.merge(official, on="team_id", how="left")
            miss = agg[agg["rank"].isna()]
            if len(miss):
                print(f"standings: R{rd} WARNING {len(miss)} team(s) not on official ranking: "
                      f"{miss.playerTeam.tolist()[:5]}")
            bad_mp = agg[(agg.off_mp.notna()) & (agg.off_mp != agg.mp)]
            bad_gp = agg[(agg.off_gp.notna()) & ((agg.off_gp * 2).round() != agg.gp_hp)]
            if len(bad_mp) or len(bad_gp):
                print(f"standings: R{rd} WARNING derived != official for "
                      f"{[(r.playerTeam, r.mp, r.off_mp) for r in bad_mp.itertuples()][:4]} (mp) "
                      f"{[(r.playerTeam, r.gp_hp, r.off_gp) for r in bad_gp.itertuples()][:4]} (gp)")
            # teams missing from the official page (shouldn't happen) get a derived rank after the rest
            if len(miss):
                nxt = int(agg["rank"].max() or 0) + 1
                agg.loc[agg["rank"].isna(), "rank"] = range(nxt, nxt + len(miss))
        agg["after_round"] = rd
        frames.append(agg[cols])

    df = pd.concat(frames, ignore_index=True)
    df["rank"] = df["rank"].astype(int)
    df.to_csv(cfg.standings_csv, index=False)
    print(f"standings: rounds 1..{completed}, {len(df)} rows "
          f"(official rank + tiebreaks) -> {cfg.standings_csv}")
    return df


def _official_ranking(cfg: EventConfig, rd: int):
    """
    chess-results ranking table after round `rd` -> DataFrame(team_id, rank,
    off_mp, tb1, tb2, tb3, off_gp) or None if unavailable. Numbers use a
    decimal comma ('135,5'); SNo is the starting number == team_id.
    """
    try:
        resp = requests.get(cfg.url(art=0, rd=rd, flag=30, zeilen=99999),
                            verify=False, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        tables = pd.read_html(StringIO(resp.text), thousands=None, decimal=",")
    except Exception as e:  # noqa: BLE001
        print(f"standings: R{rd} ranking fetch failed: {e}")
        return None
    cand = [t for t in tables
            if t.shape[0] >= 10 and {"Rk.", "SNo", "TB1", "TB2", "TB3"} <= set(map(str, t.columns))]
    if not cand:
        return None
    t = max(cand, key=lambda x: x.shape[0]).reset_index(drop=True)
    # chess-results leaves "Rk." blank on a row that ties the row above on the
    # displayed tiebreaks; the table is in rank order, so the blank row's rank
    # is its position (verified: the missing numbers == the blank positions).
    rank = pd.to_numeric(t["Rk."], errors="coerce")
    rank = rank.fillna(pd.Series(t.index + 1, index=t.index).astype(float))
    out = pd.DataFrame({
        "team_id": pd.to_numeric(t["SNo"], errors="coerce"),
        "rank": rank,
        "off_mp": pd.to_numeric(t["TB1"], errors="coerce"),
        "tb1": pd.to_numeric(t["TB2"], errors="coerce"),
        "off_gp": pd.to_numeric(t["TB3"], errors="coerce"),
        "tb3": pd.to_numeric(t.get("TB4"), errors="coerce") if "TB4" in t.columns else None,
    }).dropna(subset=["team_id", "rank"])
    out["tb2"] = out["off_gp"]
    out["team_id"] = out.team_id.astype(int)
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python chessSim/scrapeOlympiad.py <open|women>")
    cfg = get_event(sys.argv[1])
    print(f"=== Scraping {cfg.label} Olympiad {cfg.year} (tnr{cfg.tnr}) ===")
    scrape_players(cfg)
    scrape_teams(cfg)
    scrape_rounds(cfg)
    scrape_standings(cfg)
    print("done.")


if __name__ == "__main__":
    main()
