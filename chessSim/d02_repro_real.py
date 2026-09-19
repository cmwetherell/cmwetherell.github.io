"""
Ground-truth invariant check for d02pairing.pair_round, driven by the REAL sim
engine (load_event + simulate_once) so the contexts are exactly what production
sees. Wraps pair_round and asserts, per call:

  COMPLETE   every team in the (even) input appears in exactly one output pair
  NO REMATCH no output pair was already played  (checked in BOTH tuple
             orientations -- the sim passes ctx["prev"] as (a, b) AND (b, a)
             tuples, so a naive `frozenset in prev` test is vacuous)
  QUALITY    when the completeness repair fires, the round's sum|delta mp| is
             compared against the score-optimal whole-field matching, so a
             repair that hands leaders mid-table opponents shows up as a large
             excess rather than passing silently.

    python chessSim/d02_repro_real.py open 300
"""
import sys, time
from collections import defaultdict

from olympiadConfig import get_event
import simOlympiad
import d02pairing

_REAL = d02pairing.pair_round
_GLOBAL = d02pairing._global_match
S = defaultdict(int)
Q = {"repair_rounds": 0, "whole_field": 0, "excess": 0.0}


def _wrapped(ctx):
    field = ctx["teams"]; prev = ctx["prev"]; mp = ctx["mp"]
    fired = {"n": 0, "whole": 0}
    def spy(teams, opp, mp_, ir_):
        fired["n"] += 1
        if len(teams) == len(field):
            fired["whole"] += 1
        return _GLOBAL(teams, opp, mp_, ir_)
    d02pairing._global_match = spy
    try:
        pairs = _REAL(ctx)
    finally:
        d02pairing._global_match = _GLOBAL
    S["calls"] += 1

    seen = defaultdict(int)
    for p in pairs:
        a, b = tuple(p)
        seen[a] += 1; seen[b] += 1
        if (a, b) in prev or (b, a) in prev or frozenset((a, b)) in prev:
            S["rematch"] += 1
    unpaired = [t for t in field if seen[t] == 0]
    double = [t for t in field if seen[t] > 1]
    if unpaired:
        S["unpaired_calls"] += 1; S["unpaired_teams"] += len(unpaired)
    if double:
        S["double_paired"] += len(double)

    if fired["n"]:
        # a repair ran: score this round's quality vs the score-optimal matching
        Q["repair_rounds"] += 1
        Q["whole_field"] += fired["whole"]
        opp = {}
        for a, b in d02pairing._prevset(prev):
            opp.setdefault(a, set()).add(b)
        ours = sum(abs(mp[a] - mp[b]) for a, b in (tuple(p) for p in pairs))
        best = sum(abs(mp[a] - mp[b]) for a, b in
                   (tuple(p) for p in _GLOBAL(list(field), opp, mp, ctx["init_rank"])))
        Q["excess"] += ours - best
    return pairs


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "open"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    cfg = get_event(event)
    state = simOlympiad.load_event(cfg)
    simOlympiad._d02_pair_round = _wrapped
    t = time.time()
    for _ in range(n):
        simOlympiad.simulate_once(state)
    el = time.time() - t
    print(f"=== {event}: {n} REAL sims from next_round={state['next_round']} "
          f"({el:.1f}s, {el/n:.2f}s/sim single-proc) ===")
    print(f"pair calls           : {S['calls']}")
    print(f"REMATCHES            : {S['rematch']}   (must be 0)")
    print(f"UNPAIRED calls/teams : {S['unpaired_calls']}/{S['unpaired_teams']}   (must be 0)")
    print(f"DOUBLE-PAIRED teams  : {S['double_paired']}   (must be 0)")
    rr = Q["repair_rounds"]
    print(f"repair fired         : {rr} rounds ({100*rr/max(S['calls'],1):.1f}% of calls), "
          f"whole-field {Q['whole_field']}")
    if rr:
        print(f"quality excess       : mean sum|dmp| over score-optimal = "
              f"{Q['excess']/rr:.1f} per repaired round   (HEAD-style global == 0)")
    ok = S["rematch"] == 0 and S["unpaired_teams"] == 0 and S["double_paired"] == 0
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
