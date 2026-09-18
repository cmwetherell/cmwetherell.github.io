"""
Ground-truth completeness reproducer: run the REAL sim engine (load_event +
simulate_once) with d02pairing.pair_round wrapped to detect any round whose
returned pairing does not cover its even input. Counts unpaired teams per sim and
dumps failing contexts to /tmp/d02_incomplete.pkl.

    python chessSim/d02_repro_real.py open 300
"""
import sys, pickle
from collections import defaultdict

from olympiadConfig import get_event
import simOlympiad
import d02pairing

_STATS = {"unpaired_total": 0, "sims_with_bug": 0, "by_round_input_size": defaultdict(int),
          "incidents": []}
_REAL = d02pairing.pair_round


def _wrapped(ctx):
    pairs = _REAL(ctx)
    field = ctx["teams"]
    covered = set()
    for p in pairs:
        a, b = tuple(p)
        covered.add(a); covered.add(b)
    unpaired = [t for t in field if t not in covered]
    if unpaired:
        _STATS["unpaired_total"] += len(unpaired)
        _STATS["_bug_this_sim"] = True
        if len(_STATS["incidents"]) < 12:
            mp = ctx["mp"]; ir = ctx["init_rank"]
            _STATS["incidents"].append({
                "teams": list(field),
                "mp": {t: mp[t] for t in field},
                "init_rank": {t: ir[t] for t in field},
                "prev": set(ctx["prev"]),
                "unpaired": unpaired,
                "input_size": len(field),
            })
    return pairs


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "open"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    cfg = get_event(event)
    state = simOlympiad.load_event(cfg)
    # force the lazy binding to our wrapper
    simOlympiad._d02_pair_round = _wrapped
    print(f"next_round={state['next_round']} participants={len(state['participants'])}")
    for i in range(n):
        _STATS["_bug_this_sim"] = False
        simOlympiad.simulate_once(state)
        if _STATS["_bug_this_sim"]:
            _STATS["sims_with_bug"] += 1
    print(f"=== {event}: {n} REAL sims from next_round={state['next_round']} ===")
    print(f"sims with >=1 unpaired team: {_STATS['sims_with_bug']}/{n} "
          f"({100*_STATS['sims_with_bug']/n:.1f}%)")
    print(f"total unpaired-team incidents: {_STATS['unpaired_total']} "
          f"(avg {_STATS['unpaired_total']/n:.3f}/sim)")
    with open("/tmp/d02_incomplete.pkl", "wb") as f:
        pickle.dump(_STATS["incidents"], f)
    print(f"dumped {len(_STATS['incidents'])} failing contexts")
    for inc in _STATS["incidents"][:4]:
        print(f"  input {inc['input_size']} teams, {len(inc['unpaired'])} unpaired="
              f"{inc['unpaired'][:8]}, mp-range {min(inc['mp'].values())}-{max(inc['mp'].values())}")


if __name__ == "__main__":
    main()
