"""
Run the Olympiad 2026 Monte-Carlo simulation for one event and (optionally)
upload the results to Postgres for the website.

    # dry run -- simulate + aggregate + print, touch nothing in the DB:
    python chessSim/runOlympiadSims.py open --sims 2000

    # full published run -- also write teams/players/matches/runs/sims/team_summary:
    python chessSim/runOlympiadSims.py open --sims 10000 --upload
    python chessSim/runOlympiadSims.py women --sims 10000 --upload

`rounds_completed` is inferred from the scraped data (0 = pre-tournament); re-run
after scraping each round to refresh the current run. See SCHEMA.md for the
tables this writes and SIMS.md for the operating cadence.
"""

import sys
import time
import argparse
from multiprocessing import Pool, set_start_method

import numpy as np
import pandas as pd
import psycopg2
from tqdm import tqdm

from olympiadConfig import get_event
from simOlympiad import load_event, simulate_once

_STATE = None


def _init_worker(state):
    global _STATE
    _STATE = state


def _worker(_):
    return simulate_once(_STATE)


def _r1_match_rows(state):
    """Round-1 official pairings as scheduled match rows (team1 = board-1 white)."""
    tid = state["team_id"]
    rows = []
    for i, (white, black) in enumerate(state["r1_pairs"], start=1):
        rows.append({"round": 1, "board_no": i,
                     "team1_id": tid[white], "team2_id": tid[black],
                     "team1_score": None, "team2_score": None, "status": "scheduled"})
    return rows


def run(event_key, n_sims, upload, procs, chunk=500):
    cfg = get_event(event_key)
    state = load_event(cfg)
    N = state["n_teams"]
    rounds_completed = state["next_round"] - 1
    participants = state["participants"]
    team_id = state["team_id"]
    id2name = {v: k for k, v in team_id.items()}

    print(f"=== {cfg.label} Olympiad {cfg.year}: {n_sims} sims, "
          f"{len(participants)} teams, {rounds_completed} rounds completed ===")

    # Running aggregates (0-based; position p == team_id p+1).
    gold = np.zeros(N, dtype=np.int64)
    silver = np.zeros(N, dtype=np.int64)
    bronze = np.zeros(N, dtype=np.int64)
    top10c = np.zeros(N, dtype=np.int64)
    rank_sum = np.zeros(N, dtype=np.float64)
    mp_sum = np.zeros(N, dtype=np.float64)
    gp_sum = np.zeros(N, dtype=np.float64)      # half-points
    played = np.zeros(N, dtype=np.int64)

    conn = run_id = None
    db = None
    if upload:
        import olympiadDB as db
        conn = db.get_conn()
        db.ensure_schema(conn)
        db.upsert_teams(conn, cfg.key, pd.read_csv(cfg.teams_csv))
        db.upsert_players(conn, cfg.key, pd.read_csv(cfg.players_csv), team_id)
        db.upsert_matches(conn, cfg.key, _r1_match_rows(state))
        run_id = db.insert_run(conn, cfg.key, rounds_completed, n_sims, N,
                               source="pipeline")
        print(f"created run_id={run_id}")

    def db_retry(fn, what, tries=4):
        """Run a DB op, reconnecting on a dropped/stalled connection."""
        nonlocal conn
        for attempt in range(1, tries + 1):
            try:
                return fn(conn)
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                print(f"\n{what}: connection error ({e}); reconnecting "
                      f"(attempt {attempt}/{tries})")
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(min(5 * attempt, 20))
                conn = db.get_conn()
        raise RuntimeError(f"{what}: failed after {tries} attempts")

    buffer, inserted = [], 0
    start = time.time()
    with Pool(procs, initializer=_init_worker, initargs=(state,)) as pool:
        for res in tqdm(pool.imap_unordered(_worker, range(n_sims)),
                        total=n_sims, desc="sim"):
            gold[res["gold"] - 1] += 1
            silver[res["silver"] - 1] += 1
            bronze[res["bronze"] - 1] += 1
            for t in res["top10"]:
                top10c[t - 1] += 1
            fr = np.asarray(res["final_rank"], dtype=np.float64)
            rank_sum += fr
            played += (fr > 0)
            mp_sum += np.asarray(res["match_points"], dtype=np.float64)
            gp_sum += np.asarray(res["game_points"], dtype=np.float64)
            if upload:
                buffer.append(res)
                if len(buffer) >= chunk:
                    start_id, batch = inserted, buffer
                    db_retry(lambda c: db.insert_sims(c, run_id, batch, start_id=start_id),
                             f"insert_sims[{start_id}]")
                    inserted += len(buffer)
                    buffer = []
    if upload and buffer:
        start_id, batch = inserted, buffer
        db_retry(lambda c: db.insert_sims(c, run_id, batch, start_id=start_id),
                 f"insert_sims[{start_id}]")
        inserted += len(buffer)

    elapsed = time.time() - start
    print(f"simulated {n_sims} in {elapsed:.1f}s ({elapsed / n_sims * 1000:.0f} ms/sim)")

    # Per-participant summary rows.
    summary = []
    for name in participants:
        p = team_id[name] - 1
        n_played = played[p] or 1
        summary.append({
            "team_id": int(p + 1),
            "p_gold": float(gold[p] / n_sims),
            "p_silver": float(silver[p] / n_sims),
            "p_bronze": float(bronze[p] / n_sims),
            "p_medal": float((gold[p] + silver[p] + bronze[p]) / n_sims),
            "p_top10": float(top10c[p] / n_sims),
            "exp_rank": float(rank_sum[p] / n_played),
            "exp_mp": float(mp_sum[p] / n_sims),
            "exp_gp": float(gp_sum[p] / n_sims / 2.0),   # board points (0..44)
        })
    summary.sort(key=lambda s: s["p_medal"], reverse=True)

    print("\nTop 12 by P(medal):")
    print(f"{'team':32s} {'gold':>6s} {'silver':>7s} {'bronze':>7s} "
          f"{'medal':>7s} {'top10':>7s} {'E[rank]':>8s} {'E[MP]':>6s}")
    for s in summary[:12]:
        print(f"{id2name[s['team_id']][:32]:32s} "
              f"{s['p_gold']*100:5.1f}% {s['p_silver']*100:6.1f}% {s['p_bronze']*100:6.1f}% "
              f"{s['p_medal']*100:6.1f}% {s['p_top10']*100:6.1f}% "
              f"{s['exp_rank']:8.1f} {s['exp_mp']:6.1f}")

    if upload:
        db_retry(lambda c: db.insert_team_summary(c, run_id, cfg.key, summary),
                 "insert_team_summary")
        db_retry(lambda c: db.set_current(c, cfg.key, run_id), "set_current")
        db_retry(lambda c: db.prune_runs(c, cfg.key), "prune_runs")
        conn.close()
        db.revalidate()
        print(f"\nuploaded + set current: run_id={run_id}, {inserted} sims stored")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event", help="open | women")
    ap.add_argument("--sims", type=int, default=10000)
    ap.add_argument("--upload", action="store_true", help="write results to Postgres")
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()
    run(args.event, args.sims, args.upload, args.procs)


if __name__ == "__main__":
    set_start_method("spawn")
    main()
