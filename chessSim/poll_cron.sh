#!/bin/bash
# Cron wrapper for the Olympiad 2026 auto-poller. Runs from the repo root so
# python-dotenv finds .env, using the interpreter that has the sim deps.
# Install (every 15 min): see the crontab line printed by the setup, or:
#   */15 * * * * /Users/caleb/dev/pawnalyze-old-blog/chessSim/poll_cron.sh
set -euo pipefail
cd /Users/caleb/dev/pawnalyze-old-blog
PY=/Users/caleb/.pyenv/versions/3.11.4/bin/python3
mkdir -p logs
echo "===== poll $(date) =====" >> logs/olympiad_poll.log
# No caffeinate here (by request): a long re-sim can be cut off by idle sleep,
# so if a round goes unprocessed check whether the machine slept mid-update.
"$PY" chessSim/pollOlympiad.py --sims 10000 >> logs/olympiad_poll.log 2>&1
# Post-poll health check against external truth (chess-results). Writes
# logs/health/latest.md; on a NEW failure it runs `claude -p` (read-only tools)
# once to diagnose and saves logs/health/diagnosis_<ts>.md. Never blocks polling.
"$PY" chessSim/healthcheck.py >> logs/olympiad_health.log 2>&1 || true
