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
"$PY" chessSim/pollOlympiad.py --sims 10000 >> logs/olympiad_poll.log 2>&1
