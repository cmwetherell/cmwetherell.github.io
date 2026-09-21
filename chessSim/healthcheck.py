"""
Post-poll health check for the Olympiad 2026 pipeline.

Run by poll_cron.sh after every poll tick. Verifies -- against EXTERNAL truth
where possible, never against our own derived data -- that the pipeline is
alive, current, complete and accurate:

  cron_alive        the poll log ticked recently
  lock_sane         no lock held by a dead process
  fresh             every round chess-results has finalised is in the current
                    run (or an update is in progress right now)
  seeded_mp         every team's seeded match points == the chess-results
                    ranking table (TB1). This is the check that would have
                    caught both the late-arrival and the dropped-bye bugs:
                    comparing against our own standings table cannot, because
                    that table is computed from the same matches.csv.
  run_integrity     current run: one team_summary row per participant, medal
                    probabilities sum to 1
  history           exactly one pipeline run per (event, rounds_completed)
                    from 0 to current, every one with a team_summary
  no_dead_partials  no summary-less non-current run older than 6h

Writes logs/health/latest.md (always) and, on any failure, escalates ONCE per
distinct failure signature: runs `claude -p` (read-only tools) to diagnose and
saves its write-up to logs/health/diagnosis_<ts>.md. Exit 0 = healthy.

    python chessSim/healthcheck.py            # check + escalate on failure
    python chessSim/healthcheck.py --no-escalate
"""
import os, sys, time, json, hashlib, subprocess, datetime as dt
from io import StringIO

import pandas as pd
import requests

from olympiadConfig import get_event, BYE
import scrapeOlympiad as scr
import olympiadDB as db

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_DIR = os.path.join(ROOT, "logs", "health")
POLL_LOG = os.path.join(ROOT, "logs", "olympiad_poll.log")
LOCK = "/tmp/olympiad_poll.lock"
EVENTS = ("open", "women")
ESCALATE_TOOLS = "Read,Grep,Glob,Bash(git log:*),Bash(git diff:*),Bash(tail:*),Bash(ls:*)"


def _official_mp(cfg):
    """{team name: match points} from the chess-results ranking table (TB1)."""
    html = requests.get(cfg.url(art=0, flag=30, zeilen=99999), verify=False,
                        headers=scr.HEADERS, timeout=60).text
    tables = [t for t in pd.read_html(StringIO(html))
              if t.shape[0] > 50 and "TB1" in map(str, t.columns) and "Team" in map(str, t.columns)]
    if not tables:
        raise RuntimeError("ranking table (TB1) not found on chess-results")
    t = tables[0]
    return {scr._strip_team(r.Team): int(r.TB1) for r in t.itertuples(index=False)}


def _cr_completed_rounds(cfg):
    """Rounds chess-results has fully finalised, per the last scrape (round_results.csv)."""
    rr = pd.read_csv(cfg.round_results_csv)
    done = []
    for rd, g in rr.groupby("round"):
        real = g[g.team2 != BYE]
        if len(real) and (real.status == "final").all():
            done.append(int(rd))
    return max(done) if done else 0


PIPELINE_PROCS = ("pollOlympiad", "updateOlympiadRound", "runOlympiadSims", "backfill_olympiad")


def _lock_owner():
    """(alive, is_pipeline): whether the lock's owner PID exists, and whether
    it is actually a pipeline process (a manual hold such as `sleep` must not
    make the freshness check pass vacuously)."""
    try:
        pid = int(open(LOCK).read().split()[-1])
        os.kill(pid, 0)
    except (OSError, ValueError, IndexError, ProcessLookupError):
        return False, False
    try:
        cmd = subprocess.run(["ps", "-o", "command=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:  # noqa: BLE001
        cmd = ""
    return True, any(p in cmd for p in PIPELINE_PROCS)


def run_checks():
    results = []   # (name, ok, detail)

    def add(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    # cron alive: last tick in the poll log
    try:
        ticks = [l for l in open(POLL_LOG).read().splitlines() if l.startswith("===== poll ")]
        last = ticks[-1].replace("===== poll ", "").rstrip(" =")
        age_min = (dt.datetime.now() - dt.datetime.strptime(last, "%a %b %d %H:%M:%S %Z %Y")).total_seconds() / 60
        add("cron_alive", age_min < 35, f"last tick {age_min:.0f} min ago")
    except Exception as e:  # noqa: BLE001
        add("cron_alive", False, f"cannot read poll log: {e}")

    lock_held = os.path.exists(LOCK)
    owner_alive, owner_is_pipeline = _lock_owner() if lock_held else (False, False)
    add("lock_sane", (not lock_held) or owner_alive,
        "no lock" if not lock_held else
        ("held by pipeline process" if owner_is_pipeline else
         "held by a live NON-pipeline process (manual hold?)" if owner_alive else
         "STALE lock (owner dead)"))
    # Only a genuine pipeline process excuses staleness. A manual hold (e.g. a
    # `sleep` used to keep cron out during maintenance) does not -- if rounds
    # are going unprocessed behind it, that is exactly what should be flagged.
    update_running = owner_is_pipeline

    conn = db.get_conn()
    cur = conn.cursor()
    for ev in EVENTS:
        cfg = get_event(ev)
        cur.execute(f"SELECT run_id, rounds_completed, n_teams FROM {db.RUNS_TABLE} "
                    f"WHERE event=%s AND is_current", (ev,))
        row = cur.fetchone()
        if not row:
            add(f"{ev}.fresh", False, "no current run"); continue
        run_id, rc, n_teams = row

        # fresh vs chess-results
        try:
            cr_done = _cr_completed_rounds(cfg)
            ok = cr_done <= rc or update_running
            add(f"{ev}.fresh", ok, f"chess-results complete={cr_done}, current run@{rc}"
                + (" (update in progress)" if update_running and cr_done > rc else ""))
        except Exception as e:  # noqa: BLE001
            add(f"{ev}.fresh", False, f"cannot read round_results: {e}")

        # seeded MP vs the REAL ranking table
        try:
            import simOlympiad as S
            st = S.load_event(cfg)
            off = _official_mp(cfg)
            mism = [(t, st["seed_mp"][t], v) for t, v in off.items()
                    if t in st["seed_mp"] and st["seed_mp"][t] != v]
            missing = [t for t in off if t not in st["seed_mp"]]
            add(f"{ev}.seeded_mp", not mism and not missing,
                f"{len(off)} teams on chess-results; mismatches={mism[:5]} not_in_sim={missing[:5]}")
        except Exception as e:  # noqa: BLE001
            add(f"{ev}.seeded_mp", False, f"check failed: {e}")

        # current run integrity
        cur.execute(f"SELECT count(*), sum(p_gold) FROM {db.TEAM_SUMMARY_TABLE} WHERE run_id=%s", (run_id,))
        n_sum, p_gold = cur.fetchone()
        try:
            n_part = len(st["participants"])
        except Exception:  # noqa: BLE001
            n_part = None
        add(f"{ev}.run_integrity", n_sum == n_part and p_gold is not None and abs(float(p_gold) - 1) < 0.01,
            f"run {run_id}: summary rows={n_sum} participants={n_part} sum(p_gold)={float(p_gold or 0):.3f}")

        # history: one summarised pipeline run per rounds_completed 0..rc
        cur.execute(f"""
            SELECT r.rounds_completed, count(*) FROM {db.RUNS_TABLE} r
            WHERE r.event=%s AND r.source='pipeline'
              AND EXISTS (SELECT 1 FROM {db.TEAM_SUMMARY_TABLE} s WHERE s.run_id=r.run_id)
            GROUP BY 1""", (ev,))
        have = dict(cur.fetchall())
        gaps = [r for r in range(0, rc + 1) if have.get(r, 0) != 1]
        add(f"{ev}.history", not gaps, f"rounds with !=1 summarised run: {gaps}" if gaps else f"R0..R{rc} all present")

        # standings: one exact block per completed round -- ranks 1..n with no
        # gaps or duplicates, every team_id a live team, official tiebreaks set
        cur.execute(f"""
            SELECT s.after_round, count(*), count(DISTINCT s.rank), max(s.rank),
                   count(*) FILTER (WHERE t.team_id IS NULL),
                   count(*) FILTER (WHERE s.tb1 IS NULL OR s.tb1 <> s.tb1)
            FROM {db.STANDINGS_TABLE} s
            LEFT JOIN {db.TEAMS_TABLE} t ON t.event = s.event AND t.team_id = s.team_id
            WHERE s.event=%s GROUP BY 1""", (ev,))
        blocks = {r[0]: r[1:] for r in cur.fetchall()}
        bad = []
        for rd in range(1, rc + 1):
            b = blocks.get(rd)
            if b is None:
                bad.append(f"R{rd}: missing"); continue
            n, nrank, mx, orphans, notb = b
            if not (n == nrank == mx) or orphans or notb:
                bad.append(f"R{rd}: rows={n} ranks={nrank} max={mx} orphans={orphans} no_tb={notb}")
        add(f"{ev}.standings", not bad,
            "; ".join(bad) if bad else f"R1..R{rc} exact ({', '.join(str(blocks[r][0]) for r in range(1, rc + 1))} rows)")

        cur.execute(f"""
            SELECT run_id FROM {db.RUNS_TABLE} r WHERE event=%s AND NOT is_current
              AND created_at < now() - interval '6 hours'
              AND NOT EXISTS (SELECT 1 FROM {db.TEAM_SUMMARY_TABLE} s WHERE s.run_id=r.run_id)""", (ev,))
        dead = [r[0] for r in cur.fetchall()]
        add(f"{ev}.no_dead_partials", not dead, f"dead partial runs: {dead}" if dead else "none")
    conn.close()
    return results


def write_report(results):
    os.makedirs(HEALTH_DIR, exist_ok=True)
    ok_all = all(ok for _, ok, _ in results)
    lines = [f"# Olympiad pipeline health — {dt.datetime.now():%Y-%m-%d %H:%M} — "
             f"{'HEALTHY' if ok_all else 'FAILING'}", ""]
    for name, ok, detail in results:
        lines.append(f"- {'✅' if ok else '❌'} `{name}` — {detail}")
    path = os.path.join(HEALTH_DIR, "latest.md")
    open(path, "w").write("\n".join(lines) + "\n")
    return ok_all, "\n".join(lines)


def escalate(report):
    """Ask Claude (headless, read-only tools) to diagnose; once per failure signature."""
    sig = hashlib.sha1("|".join(l for l in report.splitlines() if l.startswith("- ❌")).encode()).hexdigest()[:12]
    marker = os.path.join(HEALTH_DIR, f".escalated_{sig}")
    if os.path.exists(marker):
        print(f"healthcheck: failure {sig} already escalated; not re-running claude")
        return
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M")
    out = os.path.join(HEALTH_DIR, f"diagnosis_{ts}.md")
    prompt = f"""You are on-call for the Olympiad 2026 simulation pipeline in this repo (chessSim/).
The automated health check just FAILED. Diagnose the most likely root cause and write a
concise incident report in Markdown: what is failing, the evidence you found, the probable
cause, and the exact commands a human should run to fix it. Do NOT modify anything.

Health report:
{report}

Useful sources: logs/olympiad_poll.log (tail it), chessSim/pollOlympiad.py,
chessSim/updateOlympiadRound.py, chessSim/runOlympiadSims.py, chessSim/simOlympiad.py
(load_event), chessSim/scrapeOlympiad.py, SCHEMA.md, recent `git log`.
Keep the report under 60 lines."""
    cmd = ["claude", "-p", prompt, "--allowedTools", ESCALATE_TOOLS,
           "--max-turns", "25", "--output-format", "text"]
    print(f"healthcheck: escalating failure {sig} -> {out}")
    try:
        res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        body = res.stdout if res.returncode == 0 else f"claude -p failed (rc={res.returncode})\n{res.stderr[-2000:]}"
    except Exception as e:  # noqa: BLE001
        body = f"claude -p could not run: {e}"
    open(out, "w").write(f"# Pipeline incident {ts}\n\n{report}\n\n---\n\n{body}\n")
    open(marker, "w").write(out)
    print(f"healthcheck: diagnosis written to {out}")


def main():
    escalate_on_fail = "--no-escalate" not in sys.argv
    results = run_checks()
    ok_all, report = write_report(results)
    print(report)
    if ok_all:
        # clear escalation markers so a future recurrence is reported afresh
        for f in os.listdir(HEALTH_DIR) if os.path.isdir(HEALTH_DIR) else []:
            if f.startswith(".escalated_"):
                os.remove(os.path.join(HEALTH_DIR, f))
        sys.exit(0)
    if escalate_on_fail:
        escalate(report)
    sys.exit(1)


if __name__ == "__main__":
    main()
