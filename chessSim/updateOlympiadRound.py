"""
One-command per-round update for the Olympiad 2026 pipeline.

    python chessSim/updateOlympiadRound.py open              # after a round finishes
    python chessSim/updateOlympiadRound.py women --sims 10000
    python chessSim/updateOlympiadRound.py open --backfill-games   # first mid-event run

Steps (idempotent; safe to re-run a round):
  1. Scrape players / teams / round results / standings from chess-results.
  2. Ingest board-level games (Lichess primary, chess.com backup), reconcile to
     team matches.
  3. Upsert reference + results tables: teams, players, matches (real scores +
     status), standings, games.
  4. Re-run the simulation with completed rounds held fixed and upload a fresh
     run (runs / sims / team_summary), flip is_current, prune, revalidate --
     reusing the hardened runner in runOlympiadSims.run().

The DB matches table is fed from round_results.csv (all published pairings:
final rounds with scores, plus the next round's scheduled pairings), not just
the Round-1 pairings, so `run()` is called with upsert_reference=False.
"""

import sys
import argparse

import pandas as pd

from olympiadConfig import get_event
import scrapeOlympiad as scr
import olympiadResults as results
import olympiadDB as db
import runOlympiadSims as runner


def build_match_rows(cfg):
    """round_results.csv -> match dicts for olympiadDB.upsert_matches."""
    teams = pd.read_csv(cfg.teams_csv)
    tid = {t: int(r) for t, r in zip(teams.team, teams.initRank)}
    rr = pd.read_csv(cfg.round_results_csv)
    rows = []
    for m in rr.itertuples(index=False):
        t1, t2 = tid.get(m.team1), tid.get(m.team2)
        if t1 is None or t2 is None:
            continue
        rows.append({
            "round": int(m.round), "board_no": int(m.board_no),
            "team1_id": t1, "team2_id": t2,
            "team1_score": None if pd.isna(m.team1_score_hp) else int(m.team1_score_hp),
            "team2_score": None if pd.isna(m.team2_score_hp) else int(m.team2_score_hp),
            "status": m.status,
        })
    return rows


def final_rounds(cfg):
    rr = pd.read_csv(cfg.round_results_csv)
    fin = rr[rr.status == "final"]
    return sorted(int(r) for r in fin["round"].unique())


def update(event_key, n_sims, procs, backfill_games=False):
    cfg = get_event(event_key)
    print(f"===== Updating {cfg.label} Olympiad {cfg.year} =====")

    # 1. scrape
    scr.scrape_players(cfg)
    scr.scrape_teams(cfg)
    scr.scrape_rounds(cfg)
    scr.scrape_standings(cfg)

    done_rounds = final_rounds(cfg)
    rounds_completed = done_rounds[-1] if done_rounds else 0
    print(f"completed rounds: {rounds_completed}")

    # 2. board games (latest final round by default; all of them with --backfill)
    game_rounds = done_rounds if backfill_games else ([rounds_completed] if rounds_completed else [])
    games_by_round = {}
    for rd in game_rounds:
        games_by_round[rd] = results.collect_round_games(cfg, rd)

    # 3. DB upserts (orchestrator owns reference + results tables)
    conn = db.get_conn()
    db.ensure_schema(conn)
    team_id = {t: int(r) for t, r in zip(
        pd.read_csv(cfg.teams_csv).team, pd.read_csv(cfg.teams_csv).initRank)}
    db.upsert_teams(conn, cfg.key, pd.read_csv(cfg.teams_csv))
    db.upsert_players(conn, cfg.key, pd.read_csv(cfg.players_csv), team_id)
    db.upsert_matches(conn, cfg.key, build_match_rows(cfg))

    standings = pd.read_csv(cfg.standings_csv)
    if not standings.empty:
        db.upsert_standings(conn, cfg.key, rounds_completed,
                            standings.to_dict("records"))

    for rd, gdf in games_by_round.items():
        if gdf is not None and not gdf.empty:
            db.upsert_games(conn, cfg.key, gdf.to_dict("records"))
    conn.close()

    # 4. re-run sims + upload (reference tables already handled above)
    runner.run(cfg.key, n_sims, upload=True, procs=procs, upsert_reference=False)
    print(f"===== {cfg.label}: update complete (through round {rounds_completed}) =====")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event", help="open | women")
    ap.add_argument("--sims", type=int, default=10000)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--backfill-games", action="store_true",
                    help="ingest board games for ALL completed rounds, not just the latest")
    args = ap.parse_args()
    update(args.event, args.sims, args.procs, args.backfill_games)


if __name__ == "__main__":
    from multiprocessing import set_start_method
    set_start_method("spawn")
    main()
