"""
Board-level game ingestion for the Olympiad 2026 pipeline.

Primary source: Lichess broadcasts. Lichess splits the ~400 games/round across
several overlapping feeds ("... | Open | I", "... | II", ...), so we discover all
of the event's broadcast tournaments by name, fetch each one's round PGN, and
union the games (dedup by the FIDE-id pair). chess.com is a best-effort backup.

Reconciliation attaches each board game to a chess-results team match
(round, board_no) and to white/black team_ids, using FIDE id first (players.csv
carries fide_id), with a scoped team-name fallback.

Usage is via updateOlympiadRound.py; this module has no side effects on import.
"""

import io
import re
import json

import requests
import pandas as pd
import chess.pgn

try:
    from olympiadConfig import EventConfig
except ImportError:
    from chessSim.olympiadConfig import EventConfig

LICHESS = "https://lichess.org"
HEADERS = {"User-agent": "pawnalyze-olympiad/1.0 (cmwetherell@gmail.com)"}
_RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}


def _get(url, **kw):
    return requests.get(url, headers=HEADERS, timeout=90, **kw)


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _norm(name) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


# ---------------------------------------------------------------------------
# Lichess
# ---------------------------------------------------------------------------

def discover_broadcast_tours(cfg: EventConfig):
    """Return Lichess broadcast tournament ids whose name matches this event."""
    if not cfg.lichess_broadcast_match:
        return []
    query = cfg.lichess_broadcast_match.split("|")[0].strip()  # e.g. "Samarkand 2026"
    want = cfg.lichess_broadcast_match.lower()
    try:
        data = _get(f"{LICHESS}/api/broadcast/search", params={"q": query}).json()
    except Exception as e:  # noqa: BLE001
        print(f"lichess search failed: {e}")
        return []
    results = data.get("currentPageResults", data if isinstance(data, list) else [])
    tours = []
    for item in results:
        tour = item.get("tour", item)
        name = str(tour.get("name", ""))
        if want in name.lower() and tour.get("id"):
            tours.append(tour["id"])
    return tours


def _round_ids(tour_id, rd):
    try:
        d = _get(f"{LICHESS}/api/broadcast/{tour_id}").json()
    except Exception:  # noqa: BLE001
        return []
    target = f"round {rd}"
    return [r["id"] for r in d.get("rounds", [])
            if str(r.get("name", "")).strip().lower() == target]


def _parse_pgn(pgn_text):
    games = []
    stream = io.StringIO(pgn_text)
    while True:
        try:
            game = chess.pgn.read_game(stream)
        except Exception:  # noqa: BLE001 -- a malformed game shouldn't kill the round
            continue
        if game is None:
            break
        h = game.headers
        if not h.get("White") or not h.get("Black"):
            continue
        # A fresh exporter per game -- StringExporter accumulates, so reusing one
        # would prepend every earlier game's moves to this game's pgn.
        exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
        moves = game.accept(exporter).strip()
        games.append({
            "white_player": h.get("White"), "black_player": h.get("Black"),
            "white_team": h.get("WhiteTeam"), "black_team": h.get("BlackTeam"),
            "white_fide_id": _int(h.get("WhiteFideId")),
            "black_fide_id": _int(h.get("BlackFideId")),
            "white_elo": _int(h.get("WhiteElo")), "black_elo": _int(h.get("BlackElo")),
            "result": h.get("Result") if h.get("Result") in _RESULTS else "*",
            "pgn": moves,
            "source": "lichess",
        })
    return games


def fetch_lichess_round(cfg: EventConfig, rd: int):
    """All board games for round `rd`, unioned across the event's broadcast feeds."""
    tours = discover_broadcast_tours(cfg)
    if not tours:
        print(f"lichess: no broadcast tours matched '{cfg.lichess_broadcast_match}'")
        return []
    seen, games = set(), []
    for tour in tours:
        for rid in _round_ids(tour, rd):
            try:
                pgn_text = _get(f"{LICHESS}/api/broadcast/round/{rid}.pgn").text
            except Exception as e:  # noqa: BLE001
                print(f"lichess round {rid} fetch failed: {e}")
                continue
            for g in _parse_pgn(pgn_text):
                key = (g["white_fide_id"], g["black_fide_id"],
                       _norm(g["white_player"]), _norm(g["black_player"]))
                if key in seen:
                    continue
                seen.add(key)
                games.append(g)
    print(f"lichess: {len(games)} unique games for round {rd} "
          f"across {len(tours)} feed(s)")
    return games


def fetch_chesscom_round(cfg: EventConfig, rd: int):
    """Best-effort chess.com backup. Returns [] if unavailable (never raises)."""
    if not cfg.chesscom_event_slug:
        return []
    # chess.com has no clean public broadcast PGN API; wire a source here if one
    # is identified for this event. Kept as a graceful no-op backup for now.
    return []


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile_games(cfg: EventConfig, rd: int, games: list) -> pd.DataFrame:
    """
    Attach each board game to (round, board_no, board) and white/black team_ids.
    Uses players.csv (fide_id -> team_id, roster board) and round_results.csv
    (the round's team matches -> board_no). Games that can't be reconciled to a
    match are logged and dropped (they'd violate the games->matches FK).
    """
    players = pd.read_csv(cfg.players_csv).rename(
        columns={"Bo.": "board", "Name": "name", "FideID": "fide_id", "Team": "team"})
    teams = pd.read_csv(cfg.teams_csv)
    team_id_by_name = {t: int(r) for t, r in zip(teams.team, teams.initRank)}
    team_id_by_norm = {_norm(t): int(r) for t, r in zip(teams.team, teams.initRank)}

    fide_to_team, fide_to_board = {}, {}
    roster_board = {}      # (team_id, norm player name) -> roster board
    for p in players.itertuples(index=False):
        tid = team_id_by_name.get(p.team)
        if tid is None:
            continue
        fid = _int(getattr(p, "fide_id", None))
        bo = _int(getattr(p, "board", None))
        if fid:
            fide_to_team[fid] = tid
            if bo:
                fide_to_board[fid] = bo
        roster_board[(tid, _norm(p.name))] = bo

    # round matches: {frozenset(team_ids)} -> board_no
    results = pd.read_csv(cfg.round_results_csv)
    rmatches = results[results["round"] == rd]
    match_board_no = {}
    for m in rmatches.itertuples(index=False):
        a = team_id_by_norm.get(_norm(m.team1))
        b = team_id_by_norm.get(_norm(m.team2))
        if a and b:
            match_board_no[frozenset((a, b))] = int(m.board_no)

    def resolve_team(fide, team_name):
        if fide and fide in fide_to_team:
            return fide_to_team[fide]
        return team_id_by_norm.get(_norm(team_name))

    rows, unmatched = [], 0
    for g in games:
        wt = resolve_team(g["white_fide_id"], g["white_team"])
        bt = resolve_team(g["black_fide_id"], g["black_team"])
        board_no = match_board_no.get(frozenset((wt, bt))) if (wt and bt) else None
        if board_no is None:
            unmatched += 1
            continue
        wb = fide_to_board.get(g["white_fide_id"]) or roster_board.get((wt, _norm(g["white_player"])))
        rows.append({
            "round": rd, "board_no": board_no,
            "white_team_id": wt, "black_team_id": bt,
            "white_player": g["white_player"], "black_player": g["black_player"],
            "white_fide_id": g["white_fide_id"], "black_fide_id": g["black_fide_id"],
            "white_elo": g["white_elo"], "black_elo": g["black_elo"],
            "result": g["result"], "pgn": g["pgn"], "source": g["source"],
            "_board_sort": wb if wb is not None else 99,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        print(f"reconcile: 0 games matched to a chess-results match "
              f"({unmatched} unmatched)")
        return df

    # Assign board 1..4 within each team match, ordered by roster board.
    df = df.sort_values(["board_no", "_board_sort"], kind="stable").reset_index(drop=True)
    df["board"] = df.groupby("board_no").cumcount() + 1
    df = df[df["board"] <= 4].drop(columns=["_board_sort"])
    print(f"reconcile: {len(df)} games attached to matches "
          f"({unmatched} unmatched, dropped)")
    return df


def collect_round_games(cfg: EventConfig, rd: int) -> pd.DataFrame:
    """Lichess (primary) + chess.com (backup), reconciled to matches."""
    games = fetch_lichess_round(cfg, rd)
    for g in fetch_chesscom_round(cfg, rd):     # fill any missing boards
        games.append(g)
    df = reconcile_games(cfg, rd, games)
    if not df.empty:
        df.to_csv(cfg.games_csv, index=False)
    return df
