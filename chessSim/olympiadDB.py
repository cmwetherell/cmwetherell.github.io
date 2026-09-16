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
  PRIMARY KEY (run_id, sim_id)
);

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
"""


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()


def upsert_teams(conn, event, teams_df):
    rows = [(event, int(r.initRank), str(r.fed), str(r.team),
             int(r.avg_rating), (str(r.captain) if r.captain else None))
            for r in teams_df.itertuples(index=False)]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {TEAMS_TABLE} (event, team_id, fed_code, name, avg_rating, captain)
            VALUES %s
            ON CONFLICT (event, team_id) DO UPDATE SET
              fed_code = EXCLUDED.fed_code, name = EXCLUDED.name,
              avg_rating = EXCLUDED.avg_rating, captain = EXCLUDED.captain
        """, rows)
    conn.commit()


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
             s["game_points"], s["round_scores"])
            for i, s in enumerate(sims)]
    with conn.cursor() as cur:
        execute_values(cur, f"""
            INSERT INTO {SIMS_TABLE}
              (run_id, sim_id, gold, silver, bronze, top10,
               final_rank, match_points, game_points, round_scores)
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


def set_current(conn, event, run_id):
    """Atomically make run_id the current run for this event."""
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {RUNS_TABLE} SET is_current = false "
                    f"WHERE event = %s AND is_current", (event,))
        cur.execute(f"UPDATE {RUNS_TABLE} SET is_current = true "
                    f"WHERE run_id = %s", (run_id,))
    conn.commit()


def prune_runs(conn, event, keep_latest_sims=3):
    """
    Delete raw sims for older runs to keep the table small (summaries are kept
    for history). Keeps sims for the most recent `keep_latest_sims` runs and
    always for the current run. Also removes any leftover synthetic runs.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
            DELETE FROM {SIMS_TABLE} s USING {RUNS_TABLE} r
            WHERE s.run_id = r.run_id AND r.event = %s AND NOT r.is_current
              AND r.run_id NOT IN (
                SELECT run_id FROM {RUNS_TABLE} WHERE event = %s
                ORDER BY created_at DESC LIMIT %s)
        """, (event, event, keep_latest_sims))
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
