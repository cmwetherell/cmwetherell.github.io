#!/bin/bash
# Sequenced re-run + historical backfill for the Olympiad 2026 pipeline.
# Run after a sim-input fix so every (event, rounds_completed) point on the
# odds-over-time chart is regenerated consistently. Each step is idempotent
# (prune_runs replaces the prior run for that round). Hold the poll lock while
# this runs so cron doesn't start an update on top of it.
#
#   caffeinate -i chessSim/backfill_olympiad.sh [sims] [procs]
set -uo pipefail
cd "$(dirname "$0")/.."
PY=/Users/caleb/.pyenv/versions/3.11.4/bin/python3
SIMS=${1:-10000}; PROCS=${2:-8}
step() { echo; echo "######## $(date '+%H:%M:%S')  $*"; }

# 1. current runs first (what visitors see)
for ev in open women; do
  step "CURRENT $ev"
  $PY -u chessSim/updateOlympiadRound.py $ev --sims $SIMS --procs $PROCS || echo "!! CURRENT $ev FAILED"
done

# 2. history, newest first. Round 0 == pre-tournament.
#    Current rounds_completed is skipped (already regenerated above).
for ev in open women; do
  cur=$($PY -c "
import sys; sys.path.insert(0,'chessSim'); import olympiadDB as db
c=db.get_conn(); cur=c.cursor()
cur.execute('SELECT rounds_completed FROM olympiad_2026_runs WHERE event=%s AND is_current',('$ev',))
print(cur.fetchone()[0]); c.close()" 2>/dev/null)
  for ((rd=cur-1; rd>=0; rd--)); do
    step "BACKFILL $ev through R$rd"
    $PY -u chessSim/runOlympiadSims.py $ev --sims $SIMS --procs $PROCS --upload --through-round $rd \
      || echo "!! BACKFILL $ev R$rd FAILED"
  done
done

step "ALL DONE"
