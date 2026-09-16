"""
Auto-poller for the Olympiad 2026 pipeline.

Run on a schedule (e.g. every 15 min via cron). For each event it cheaply checks
how many rounds are FULLY completed on chess-results and, if that is beyond the
round the current DB run already reflects, runs the full per-round update
(updateOlympiadRound.update) which re-simulates and uploads.

    python chessSim/pollOlympiad.py            # both events, 10k sims
    python chessSim/pollOlympiad.py --sims 5000

Guards:
  - A round counts as complete only when EVERY match in it is final (never acts
    on a half-played/live round).
  - A lock file prevents overlapping runs (an update takes several minutes).
  - No-ops (and says so) when there is nothing new -- safe to run every 15 min
    for the whole event.
"""

import os
import sys
import time
import argparse

import pandas as pd

from olympiadConfig import get_event, EVENTS
import scrapeOlympiad as scr
import olympiadDB as db
from updateOlympiadRound import update

_LOCK = "/tmp/olympiad_poll.lock"
_LOCK_STALE_SECONDS = 3600   # ignore a lock older than this (crashed run)


def _acquire_lock():
    if os.path.exists(_LOCK):
        age = time.time() - os.path.getmtime(_LOCK)
        if age < _LOCK_STALE_SECONDS:
            return False
    with open(_LOCK, "w") as fh:
        fh.write(str(os.getpid()))
    return True


def _release_lock():
    try:
        os.remove(_LOCK)
    except OSError:
        pass


def fully_completed_round(cfg) -> int:
    """Highest round on chess-results where every match is final (0 if none)."""
    scr.scrape_rounds(cfg)   # writes round_results.csv (only hits art=2 pages)
    rr = pd.read_csv(cfg.round_results_csv)
    if rr.empty:
        return 0
    best = 0
    for rd, grp in rr.groupby("round"):
        if len(grp) > 0 and (grp["status"] == "final").all():
            best = max(best, int(rd))
    return best


def db_rounds_completed(cfg) -> int:
    """rounds_completed of the current run for this event, or -1 if none."""
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout='15000'")
            cur.execute(
                f"SELECT rounds_completed FROM {db.RUNS_TABLE} "
                f"WHERE event = %s AND is_current", (cfg.key,))
            row = cur.fetchone()
        return int(row[0]) if row else -1
    finally:
        conn.close()


def poll_once(n_sims, procs):
    updated = []
    for key in EVENTS:
        cfg = get_event(key)
        try:
            done = fully_completed_round(cfg)
            have = db_rounds_completed(cfg)
        except Exception as e:  # noqa: BLE001 -- one event's hiccup shouldn't block the other
            print(f"{key}: check failed ({e}); skipping this tick")
            continue
        if done > have:
            print(f"{key}: round {done} complete (current run at {have}) -> UPDATING")
            update(key, n_sims, procs)
            updated.append((key, done))
        else:
            print(f"{key}: nothing new (complete={done}, current run={have})")
    return updated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=10000)
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()

    if not _acquire_lock():
        print("another poll/update is running (lock held); exiting")
        return
    try:
        updated = poll_once(args.sims, args.procs)
        print(f"poll done; updated: {updated or 'none'}")
    finally:
        _release_lock()


if __name__ == "__main__":
    from multiprocessing import set_start_method
    set_start_method("spawn")
    main()
