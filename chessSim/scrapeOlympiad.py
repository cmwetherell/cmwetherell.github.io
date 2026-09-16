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
    from olympiadConfig import get_event, EventConfig
except ImportError:  # when run as chessSim.scrapeOlympiad
    from chessSim.olympiadConfig import get_event, EventConfig

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


def _strip_team(name) -> str:
    return str(name).replace("*)", "").strip()


def _is_real_team(name: str) -> bool:
    return bool(name) and name.lower() not in _NON_TEAM


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
    Current team standings after the last completed round, computed from the
    scraped completed matches (authoritative match scores from chess-results):
    match points and game points per team, ranked by (MP desc, GP desc).

    Columns: after_round, team_id, rank, mp, gp_hp, tb1, tb2, tb3.
    tb1..tb3 (official Sonneborn-Berger tiebreaks) are left null here; the exact
    official ordering can be layered in from the chess-results ranking crosstable
    once it is published (it does not exist until a round is final). Empty
    pre-tournament.
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

    after_round = int(matches["round"].max())
    agg = matches.groupby("playerTeam").agg(
        mp=("gp", lambda s: int(sum(_gp_to_mp(g) for g in s))),
        gp_hp=("gp", lambda s: int(round(s.sum() * 2))),
    ).reset_index()
    agg = agg.sort_values(["mp", "gp_hp"], ascending=False).reset_index(drop=True)
    agg["rank"] = agg.index + 1

    rows = []
    for r in agg.itertuples(index=False):
        tid = team_id.get(r.playerTeam)
        if tid is None:
            continue
        rows.append({"after_round": after_round, "team_id": tid, "rank": int(r.rank),
                     "mp": int(r.mp), "gp_hp": int(r.gp_hp),
                     "tb1": None, "tb2": None, "tb3": None})
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(cfg.standings_csv, index=False)
    print(f"standings: after round {after_round}, {len(df)} teams -> {cfg.standings_csv}")
    return df


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
