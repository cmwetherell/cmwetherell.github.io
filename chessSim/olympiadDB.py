"""
Postgres access for Olympiad 2026 simulations.

Owns the schema (idempotent DDL), reference-table upserts (teams, players,
matches) and the simulation writes (runs / sims / team_summary). All credentials
come from the repo-root .env via python-dotenv -- see .env.example. Nothing here
takes DB credentials as arguments or hardcodes them.

Table shapes are documented for the website team in SCHEMA.md; keep the two in
sync when changing DDL here.
"""

import os
import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from olympiadConfig import (
    TEAMS_TABLE, PLAYERS_TABLE, MATCHES_TABLE,
    RUNS_TABLE, SIMS_TABLE, TEAM_SUMMARY_TABLE,
    GAMES_TABLE, STANDINGS_TABLE,
)

load_dotenv()

# Optional: URL to ping after an upload so the site drops its cached data.
REVALIDATE_URL = os.getenv("REVALIDATE_URL", "https://www.pawnalyze.com/revalidate")


def get_conn():
    # keepalives + statement_timeout are essential: without them a dropped Neon
    # connection leaves psycopg2 blocked on a dead socket forever (observed as a
    # 30+ min hang mid-upload). keepalives detect a dead peer in ~80s; the
    # server-side statement_timeout caps any single statement at 3 min.
    conn = psycopg2.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DATABASE"),
        sslmode="require",
        connect_timeout=30,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )
    # Server-side cap per statement (set via SET, not libpq options, so it works
    # through Neon's connection pooler too).
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = 180000")
    conn.commit()
    return conn


DDL = f"""
CREATE TABLE IF NOT EXISTS {TEAMS_TABLE} (
  event text NOT NULL CHECK (event IN ('open','women')),
  team_id smallint NOT NULL,
  fed_code text NOT NULL,
  name text NOT NULL,
  avg_rating smallint NOT NULL,
  captain text,
  PRIMARY KEY (event, team_id)
);

CREATE TABLE IF NOT EXISTS {PLAYERS_TABLE} (
  event text NOT NULL,
  team_id smallint NOT NULL,
  board smallint NOT NULL CHECK (board BETWEEN 1 AND 6),
  name text NOT NULL,
  title text,
  rating smallint NOT NULL,
  fide_id integer,
  PRIMARY KEY (event, team_id, board),
  FOREIGN KEY (event, team_id) REFERENCES {TEAMS_TABLE} (event, team_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS {MATCHES_TABLE} (
  event text NOT NULL CHECK (event IN ('open','women')),
  round smallint NOT NULL CHECK (round BETWEEN 1 AND 11),
  board_no smallint NOT NULL,
  team1_id smallint NOT NULL,
  team2_id smallint,
  team1_score smallint CHECK (team1_score BETWEEN 0 AND 8),
  team2_score smallint CHECK (team2_score BETWEEN 0 AND 8),
  status text NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled','live','final')),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event, round, board_no)
);
CREATE INDEX IF NOT EXISTS {MATCHES_TABLE}_status ON {MATCHES_TABLE} (event, round, status);

CREATE TABLE IF NOT EXISTS {RUNS_TABLE} (
  run_id serial PRIMARY KEY,
  event text NOT NULL CHECK (event IN ('open','women')),
  rounds_completed smallint NOT NULL CHECK (rounds_completed BETWEEN 0 AND 11),
  n_sims integer NOT NULL,
  n_teams smallint NOT NULL,
  source text NOT NULL DEFAULT 'pipeline' CHECK (source IN ('pipeline','synthetic')),
  is_current boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  notes text
);
CREATE UNIQUE INDEX IF NOT EXISTS {RUNS_TABLE}_current ON {RUNS_TABLE} (event) WHERE is_current;
CREATE INDEX IF NOT EXISTS {RUNS_TABLE}_hist ON {RUNS_TABLE} (event, rounds_completed, created_at DESC);

CREATE TABLE IF NOT EXISTS {SIMS_TABLE} (
  run_id integer NOT NULL REFERENCES {RUNS_TABLE} ON DELETE CASCADE,
  sim_id integer NOT NULL,
  gold smallint NOT NULL,
  silver smallint NOT NULL,
  bronze smallint NOT NULL,
  top10 smallint[] NOT NULL,
  final_rank smallint[] NOT NULL,
  match_points smallint[] NOT NULL,
  game_points smallint[] NOT NULL,
  round_scores smallint[] NOT NULL,
  round_opps smallint[],
  PRIMARY KEY (run_id, sim_id)
);
-- round_opps added after initial deploy; idempotent for existing tables.
ALTER TABLE {SIMS_TABLE} ADD COLUMN IF NOT EXISTS round_opps smallint[];

CREATE TABLE IF NOT EXISTS {TEAM_SUMMARY_TABLE} (
  run_id integer NOT NULL REFERENCES {RUNS_TABLE} ON DELETE CASCADE,
  event text NOT NULL,
  team_id smallint NOT NULL,
  p_gold real NOT NULL,
  p_silver real NOT NULL,
  p_bronze real NOT NULL,
  p_medal real NOT NULL,
  p_top10 real NOT NULL,
  exp_rank real NOT NULL,
  exp_mp real NOT NULL,
  exp_gp real NOT NULL,
  PRIMARY KEY (run_id, team_id)
);

CREATE TABLE IF NOT EXISTS {STANDINGS_TABLE} (
  event text NOT NULL CHECK (event IN ('open','women')),
  after_round smallint NOT NULL CHECK (after_round BETWEEN 0 AND 11),
  team_id smallint NOT NULL,
  rank smallint NOT NULL,
  mp smallint NOT NULL,
  gp_hp smallint NOT NULL,               -- game points in half-points
  tb1 real, tb2 real, tb3 real,
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event, after_round, team_id)
);

CREATE TABLE IF NOT EXISTS {GAMES_TABLE} (
  event text NOT NULL CHECK (event IN ('open','women')),
  round smallint NOT NULL CHECK (round BETWEEN 1 AND 11),
  board_no smallint NOT NULL,            -- team-match number (FK to matches)
  board smallint NOT NULL CHECK (board BETWEEN 1 AND 4),
  white_team_id smallint,
  black_team_id smallint,
  white_player text,
  black_player text,
  white_fide_id integer,
  black_fide_id integer,
  white_elo smallint,
  black_elo smallint,
  result text CHECK (result IN ('1-0','1/2-1/2','0-1','*')),
  pgn text,                              -- moves, for the game viewer
  source text NOT NULL DEFAULT 'lichess' CHECK (source IN ('lichess','chesscom','chess-results')),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event, round, board_no, board),
  FOREIGN KEY (event, round, board_no) REFERENCES {MATCHES_TABLE} (event, round, board_no) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS {GAMES_TABLE}_fide ON {GAMES_TABLE} (white_fide_id, black_fide_id);
"""


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()


def upsert_teams(conn, event, teams_df):
    """
    Upsert the entry list and PRUNE trailing rows beyond it. team_id is the
    chess-results starting number, which shifted for the last few entries while
    the list was still settling before R1 (a team added then removed pushed
    "US Virgin Islands" through 191/190/189); without pruning, each renumbering
    leaves a ghost row under the old id (players cascade via the FK).
    """
    rows = [(event, int(r.initRank), str(r.fed), str(r.team),
             int(r.avg_rating), (str(r.captain) if r.captain else None))
            for r in teams_df.itertuples(index=False)]
    n_teams = max(r[1] for r in rows)
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {TEAMS_TABLE} (event, team_id, fed_code, name, avg_rating, captain)
            VALUES %s
            ON CONFLICT (event, team_id) DO UPDATE SET
              fed_code = EXCLUDED.fed_code, name = EXCLUDED.name,
              avg_rating = EXCLUDED.avg_rating, captain = EXCLUDED.captain
        """, rows)
        cur.execute(f"DELETE FROM {TEAMS_TABLE} WHERE event = %s AND team_id > %s",
                    (event, n_teams))
        if cur.rowcount:
            print(f"teams: pruned {cur.rowcount} stale row(s) with team_id > {n_teams}")
    conn.commit()


def last_run_n_teams(conn, event):
    """n_teams of the most recent run for this event (None if no runs yet)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT n_teams FROM {RUNS_TABLE} WHERE event = %s "
                    f"ORDER BY created_at DESC LIMIT 1", (event,))
        row = cur.fetchone()
    return int(row[0]) if row else None


def upsert_players(conn, event, players_df, team_id):
    """team_id: dict mapping team name -> team_id (snr)."""
    # Rename to valid identifiers first ("Bo." breaks itertuples attribute access).
    df = players_df.rename(columns={
        "Bo.": "board", "Name": "name", "Title": "title",
        "Rtg": "rating", "FideID": "fide_id", "Team": "team"})
    rows = []
    for r in df.itertuples(index=False):
        tid = team_id.get(r.team)
        if tid is None:
            continue
        try:
            board = int(r.board)
        except (TypeError, ValueError):
            continue
        if board < 1 or board > 6:
            continue
        title = getattr(r, "title", None)
        title = None if (title is None or pd.isna(title)) else str(title)
        try:
            fide = int(r.fide_id)
        except (TypeError, ValueError):
            fide = None
        rows.append((event, tid, board, str(r.name), title, int(r.rating), fide))
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {PLAYERS_TABLE} (event, team_id, board, name, title, rating, fide_id)
            VALUES %s
            ON CONFLICT (event, team_id, board) DO UPDATE SET
              name = EXCLUDED.name, title = EXCLUDED.title,
              rating = EXCLUDED.rating, fide_id = EXCLUDED.fide_id
        """, rows)
    conn.commit()


def upsert_matches(conn, event, match_rows):
    """
    match_rows: list of dicts with keys round, board_no, team1_id, team2_id,
    team1_score, team2_score (half-points or None), status.
    """
    rows = [(event, m["round"], m["board_no"], m["team1_id"], m.get("team2_id"),
             m.get("team1_score"), m.get("team2_score"), m.get("status", "scheduled"))
            for m in match_rows]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {MATCHES_TABLE}
              (event, round, board_no, team1_id, team2_id, team1_score, team2_score, status)
            VALUES %s
            ON CONFLICT (event, round, board_no) DO UPDATE SET
              team1_id = EXCLUDED.team1_id, team2_id = EXCLUDED.team2_id,
              team1_score = EXCLUDED.team1_score, team2_score = EXCLUDED.team2_score,
              status = EXCLUDED.status, updated_at = now()
        """, rows)
    conn.commit()


def upsert_standings(conn, event, after_round, rows):
    """rows: dicts with team_id, rank, mp, gp_hp, tb1, tb2, tb3 and optionally
    after_round (rows may span several rounds; a row without it uses the
    `after_round` argument). NaN tiebreaks are stored as NULL."""
    def _f(v):
        return None if v is None or (isinstance(v, float) and v != v) else float(v)
    vals = [(event, int(r.get("after_round", after_round)), int(r["team_id"]), int(r["rank"]),
             int(r["mp"]), int(r["gp_hp"]), _f(r.get("tb1")), _f(r.get("tb2")), _f(r.get("tb3")))
            for r in rows]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {STANDINGS_TABLE}
              (event, after_round, team_id, rank, mp, gp_hp, tb1, tb2, tb3)
            VALUES %s
            ON CONFLICT (event, after_round, team_id) DO UPDATE SET
              rank = EXCLUDED.rank, mp = EXCLUDED.mp, gp_hp = EXCLUDED.gp_hp,
              tb1 = EXCLUDED.tb1, tb2 = EXCLUDED.tb2, tb3 = EXCLUDED.tb3,
              updated_at = now()
        """, vals)
    conn.commit()


def upsert_games(conn, event, rows):
    """
    rows: dicts with round, board_no, board, white_team_id, black_team_id,
    white_player, black_player, white_fide_id, black_fide_id, white_elo,
    black_elo, result, pgn, source.
    """
    vals = [(event, r["round"], r["board_no"], r["board"],
             r.get("white_team_id"), r.get("black_team_id"),
             r.get("white_player"), r.get("black_player"),
             r.get("white_fide_id"), r.get("black_fide_id"),
             r.get("white_elo"), r.get("black_elo"),
             r.get("result"), r.get("pgn"), r.get("source", "lichess"))
            for r in rows]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {GAMES_TABLE}
              (event, round, board_no, board, white_team_id, black_team_id,
               white_player, black_player, white_fide_id, black_fide_id,
               white_elo, black_elo, result, pgn, source)
            VALUES %s
            ON CONFLICT (event, round, board_no, board) DO UPDATE SET
              white_team_id = EXCLUDED.white_team_id, black_team_id = EXCLUDED.black_team_id,
              white_player = EXCLUDED.white_player, black_player = EXCLUDED.black_player,
              white_fide_id = EXCLUDED.white_fide_id, black_fide_id = EXCLUDED.black_fide_id,
              white_elo = EXCLUDED.white_elo, black_elo = EXCLUDED.black_elo,
              result = EXCLUDED.result, pgn = EXCLUDED.pgn, source = EXCLUDED.source,
              updated_at = now()
        """, vals, page_size=200)
    conn.commit()


def insert_run(conn, event, rounds_completed, n_sims, n_teams,
               source="pipeline", notes=None):
    """Create a run row (is_current stays false until set_current)."""
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO {RUNS_TABLE}
              (event, rounds_completed, n_sims, n_teams, source, is_current, notes)
            VALUES (%s, %s, %s, %s, %s, false, %s)
            RETURNING run_id
        """, (event, rounds_completed, n_sims, n_teams, source, notes))
        run_id = cur.fetchone()[0]
    conn.commit()
    return run_id


def insert_sims(conn, run_id, sims, start_id=0, page_size=500):
    """sims: list of dicts from simOlympiad.simulate_once; sim_id = start_id + i."""
    rows = [(run_id, start_id + i,
             s["gold"], s["silver"], s["bronze"],
             s["top10"], s["final_rank"], s["match_points"],
             s["game_points"], s["round_scores"], s["round_opps"])
            for i, s in enumerate(sims)]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {SIMS_TABLE}
              (run_id, sim_id, gold, silver, bronze, top10,
               final_rank, match_points, game_points, round_scores, round_opps)
            VALUES %s
            ON CONFLICT (run_id, sim_id) DO NOTHING
        """, rows, page_size=page_size)
    conn.commit()


def insert_team_summary(conn, run_id, event, summary_rows):
    """summary_rows: list of dicts keyed team_id, p_gold, ... exp_gp."""
    rows = [(run_id, event, s["team_id"], s["p_gold"], s["p_silver"], s["p_bronze"],
             s["p_medal"], s["p_top10"], s["exp_rank"], s["exp_mp"], s["exp_gp"])
            for s in summary_rows]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {TEAM_SUMMARY_TABLE}
              (run_id, event, team_id, p_gold, p_silver, p_bronze,
               p_medal, p_top10, exp_rank, exp_mp, exp_gp)
            VALUES %s
        """, rows)
    conn.commit()


def validate_round_opps(conn, run_id, event, n_teams, n_rounds=11, sample=60,
                        max_official_round=99):
    """
    Verify round_opps on a run before it is made current. Raises AssertionError
    (with all failures) if any check fails; returns a short summary dict on pass.
    Checks: no NULLs, correct 2-D dims on every row, and on a sample of sims --
    symmetry, no repeated opponent within a sim, round_scores agree with pairings,
    and round 1 (+ any completed round) matches olympiad_2026_matches.
    """
    errs = []
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout='60000'")
        # 1. no NULL, correct dims on EVERY row
        cur.execute(f"""
            SELECT count(*) FROM {SIMS_TABLE}
            WHERE run_id = %s AND (round_opps IS NULL
              OR array_length(round_opps,1) <> %s
              OR array_length(round_opps,2) <> %s)
        """, (run_id, n_rounds, n_teams))
        bad = cur.fetchone()[0]
        if bad:
            errs.append(f"{bad} rows with NULL/wrong-shaped round_opps")

        # official pairings per completed/published round (from matches)
        cur.execute(f"""
            SELECT round, team1_id, team2_id, team1_score FROM {MATCHES_TABLE}
            WHERE event = %s
        """, (event,))
        official, final_rounds = {}, set()
        for rnd, t1, t2, sc in cur.fetchall():
            official.setdefault(rnd, {})[t1] = t2
            official[rnd][t2] = t1
            if sc is not None:
                final_rounds.add(rnd)   # a real, played round (may have forfeits)

        # Teams the sim actually simulates (participants). A team whose OFFICIAL
        # opponent isn't a participant (its opponent joined/left between rounds)
        # can't be reproduced, so we don't require an official match for it.
        cur.execute(f"SELECT team_id FROM {TEAM_SUMMARY_TABLE} WHERE run_id = %s", (run_id,))
        participants = {r[0] for r in cur.fetchall()}

        # sample of sims for content checks
        cur.execute(f"""
            SELECT sim_id, round_opps, round_scores FROM {SIMS_TABLE}
            WHERE run_id = %s ORDER BY sim_id LIMIT %s
        """, (run_id, sample))
        rows = cur.fetchall()

    for sim_id, opps, scores in rows:
        for r in range(n_rounds):
            seen = {}
            for t0 in range(n_teams):
                opp = opps[r][t0]
                if opp == 0 or opp == -1:
                    continue
                tid = t0 + 1
                # symmetry
                if opps[r][opp - 1] != tid:
                    errs.append(f"sim {sim_id} r{r+1}: opp asymmetry t{tid}->{opp}")
                # score agreement: simulated rounds always play 4 boards (==8);
                # real completed rounds can total <8 due to forfeited boards.
                ssum = scores[r][t0] + scores[r][opp - 1]
                if (r + 1) in final_rounds:
                    if not (0 <= ssum <= 8):
                        errs.append(f"sim {sim_id} r{r+1}: real scores out of range {ssum}")
                elif ssum != 8:
                    errs.append(f"sim {sim_id} r{r+1}: sim scores !=8 ({ssum}) for t{tid}/{opp}")
                # official pairing match -- only for rounds the sim actually pins
                # to official (<= max_official_round; later rounds are forecast),
                # and only when the official opponent is a participant.
                off = official.get(r + 1) if (r + 1) <= max_official_round else None
                if (off and off.get(tid) is not None and off[tid] in participants
                        and off[tid] != opp):
                    errs.append(f"sim {sim_id} r{r+1}: t{tid} opp {opp} != official {off[tid]}")
                seen[tid] = seen.get(tid, 0) + 1
            # no team appears twice as a player in a round is implicit; check repeats below
        # no repeated opponent across the whole sim, per team
        for t0 in range(n_teams):
            os_ = [opps[r][t0] for r in range(n_rounds) if opps[r][t0] > 0]
            if len(os_) != len(set(os_)):
                errs.append(f"sim {sim_id}: team {t0+1} has a repeat opponent")
        if len(errs) > 20:
            break

    if errs:
        raise AssertionError(f"round_opps validation failed ({len(errs)} issues): "
                             + "; ".join(errs[:20]))
    return {"rows_checked": len(rows), "dims": f"{n_rounds}x{n_teams}",
            "official_rounds": sorted(official)}


def set_current(conn, event, run_id):
    """Atomically make run_id the current run for this event."""
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {RUNS_TABLE} SET is_current = false "
                    f"WHERE event = %s AND is_current", (event,))
        cur.execute(f"UPDATE {RUNS_TABLE} SET is_current = true "
                    f"WHERE run_id = %s", (run_id,))
    conn.commit()


def prune_runs(conn, event, past_sims_keep=10000):
    """
    Storage control. The CURRENT run keeps its full sim set (which may be raised
    above the baseline for extra pick-em precision). Every OTHER run of this event
    is capped at `past_sims_keep` sims (default 10k) -- so if a round is simulated
    with more, it's trimmed back once it's no longer the current round (sims are
    i.i.d., so keeping sim_id < N is a valid random subsample). Run rows and
    team_summary are kept for ALL runs, so the odds-over-time history (which reads
    team_summary, not raw sims) is fully preserved. Drops synthetic runs.
    """
    with conn.cursor() as cur:
        # 1. Drop dead partial runs: a run row with no team_summary is a crash
        # leftover (the runner writes the summary last, just before set_current).
        # Such a run must never be allowed to shadow a real one -- step 2 keeps
        # the NEWEST run per rounds_completed, and a newer summary-less partial
        # would otherwise win and delete the good run (this happened to Women R3).
        # The age guard protects a run that is legitimately still in flight from
        # another process (a full run takes well under an hour).
        cur.execute(f"""
            DELETE FROM {RUNS_TABLE} r
            WHERE r.event = %s AND NOT r.is_current
              AND r.created_at < now() - interval '6 hours'
              AND NOT EXISTS (SELECT 1 FROM {TEAM_SUMMARY_TABLE} s WHERE s.run_id = r.run_id)
        """, (event,))
        # 2. Drop superseded runs: keep only the latest COMPLETE run per
        # rounds_completed (plus the current run). Re-running a round replaces
        # its prior run so the odds-history has exactly one point per (event,
        # rounds_completed). Only a run that has a team_summary can supersede
        # another. Sims cascade-delete via FK.
        cur.execute(f"""
            DELETE FROM {RUNS_TABLE} r
            WHERE r.event = %s AND NOT r.is_current AND EXISTS (
                SELECT 1 FROM {RUNS_TABLE} r2
                WHERE r2.event = r.event AND r2.rounds_completed = r.rounds_completed
                  AND r2.run_id <> r.run_id
                  AND (r2.is_current OR r2.created_at > r.created_at)
                  AND EXISTS (SELECT 1 FROM {TEAM_SUMMARY_TABLE} s2 WHERE s2.run_id = r2.run_id))
        """, (event,))
        # Cap non-current runs at past_sims_keep sims.
        cur.execute(f"""
            DELETE FROM {SIMS_TABLE} s USING {RUNS_TABLE} r
            WHERE s.run_id = r.run_id AND r.event = %s
              AND NOT r.is_current AND s.sim_id >= %s
        """, (event, past_sims_keep))
        cur.execute(f"DELETE FROM {RUNS_TABLE} WHERE event = %s AND source = 'synthetic'",
                    (event,))
    conn.commit()


def revalidate():
    if not REVALIDATE_URL:
        return
    try:
        r = requests.get(REVALIDATE_URL, timeout=30)
        print(f"revalidate: {REVALIDATE_URL} -> {r.status_code}")
    except Exception as e:  # noqa: BLE001
        print(f"revalidate failed ({e}); site cache may be stale until next deploy")
