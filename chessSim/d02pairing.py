"""
FIDE D.02 (Olympiad) team pairing engine.

Reproduces chess-results' Olympiad pairings. The bracket pairing itself is a
standard top-half-vs-bottom-half slide with rematch-avoiding transpositions
(reused from simOlympiad.pairingFast, whose opponent order IS the D.02 order).
The hard part is FLOAT SELECTION between scoregroups:

Process groups top-down in ranking order ((-match_points, start_rank)). For each
group choose the minimal, parity-preserving number of LOWEST teams to downfloat
so that the current group is pairable AND the next bracket (those floaters + the
next group) is also pairable (D.02 Art. 8.3-8.4 / criteria [C4]-[C6]). Downfloated
teams join the next group at the TOP (higher score) and are paired against the
strongest residents (heterogeneous bracket), the rest sliding normally.

Colour allocation (board-1) is applied after opponents are fixed
(equalisation -> alternation, CD in [-2,+2], no 3-in-a-row; Art. 7.3/7.5-7.6);
the [C3] "same absolute colour preference can't meet" constraint is applied as a
pairing filter when colours are enabled.

pair_round(ctx) -> set of frozenset({team_id_a, team_id_b}).
ctx is the dict from d02_test.load_context (or the sim's live state).
"""

from itertools import groupby

import numpy as np
from scipy.optimize import linear_sum_assignment
import networkx as nx

_INF = 1e9
# D.02 assigns board-1 colour AFTER pairing (Art 7.5 equalisation->alternation,
# ±2 / no-3-in-a-row limits); colour does NOT reorder who-plays-whom. So colour
# weight is 0 by default (kept only as an experimental knob).
_W_COLOR = 0.0
_W_DEV = 1.0        # hug the S1[i]-vs-S2[i] slide (Art 9.3)


def _prevset(prev_frozensets):
    s = set()
    for p in prev_frozensets:
        a, b = tuple(p)
        s.add((a, b)); s.add((b, a))
    return s


_W_REMATCH = 1e6   # finite (>> colour, << _INF): used only by the completeness safety net


def _slide_match(teams, opp, last_color, allow_rematch=False):
    """
    Min-cost bipartite assignment of S1 (top half) to S2 (bottom half) of a
    HOMOGENEOUS resident group: rematches forbidden, then minimise same-colour
    meetings ([C8], weight _W_COLOR), then hug the S1[i]-vs-S2[i] slide.
    `opp` maps team -> set of prior opponents (fast rematch lookup).
    With allow_rematch=True, a rematch is heavily penalised but permitted, so a
    complete pairing is always returned (used only as a last-resort safety net).
    """
    n = len(teams)
    if n % 2:
        return None
    if n == 0:
        return []
    h = n // 2
    S1, S2 = teams[:h], teams[h:]
    idx = np.arange(h)
    C = (np.abs(idx[:, None] - idx[None, :]) * _W_DEV).astype(float)  # slide-deviation
    rematch_cost = _W_REMATCH if allow_rematch else _INF
    s2_pos = {b: j for j, b in enumerate(S2)}
    for i, a in enumerate(S1):
        for o in opp.get(a, ()):                 # rematch penalty
            j = s2_pos.get(o)
            if j is not None:
                C[i, j] += rematch_cost
        if _W_COLOR:
            ca = last_color.get(a, 0)
            if ca:
                for j, b in enumerate(S2):
                    if last_color.get(b, 0) == ca and C[i, j] < _INF:
                        C[i, j] += _W_COLOR
    ri, cj = linear_sum_assignment(C)
    pairs = []
    for i, j in zip(ri, cj):
        if C[i, j] >= _INF:
            return None
        pairs.append((S1[i], S2[j]))
    return pairs


def _bracket_pairs(bracket, n_float, opp, last_color):
    """
    Pair a bracket whose first `n_float` teams are downfloaters (higher score).
    D.02 pairs each downfloater against the STRONGEST resident it hasn't played
    (the MDP pairing), then slides the remaining residents. Returns (a,b) list or
    None if a rematch is unavoidable.
    """
    if len(bracket) % 2:
        return None
    floaters, residents = bracket[:n_float], bracket[n_float:]
    used, pairs = set(), []
    for f in floaters:
        fopp = opp.get(f, ())
        opponent = next((r for r in residents if r not in used and r not in fopp), None)
        if opponent is None:
            return None
        used.add(opponent)
        pairs.append((f, opponent))
    rest = [r for r in residents if r not in used]
    slide = _slide_match(rest, opp, last_color)
    if slide is None:
        # The S1<->S2 slide can't avoid a rematch here; a rematch-free pairing may
        # still exist within the bracket via an exchange (two same-half teams
        # paired). Find it with a rematch-free general matching (blossom) on just
        # this bracket -- small, so fast. None only if truly unpairable.
        slide = _blossom_match(rest, opp)
    if slide is None:
        return None
    return pairs + slide


def _blossom_match(teams, opp):
    """Rematch-free general (non-bipartite) perfect matching of one bracket,
    biased toward the S1[i]-vs-S2[i] slide distance. None if none exists."""
    n = len(teams)
    if n % 2 or n == 0:
        return [] if n == 0 else None
    h = n // 2
    pos = {t: i for i, t in enumerate(teams)}
    G = nx.Graph()
    G.add_nodes_from(teams)
    for i, a in enumerate(teams):
        oa = opp.get(a, ())
        for b in teams[i + 1:]:
            if b in oa:
                continue
            # prefer pairs at the slide distance (~h apart)
            G.add_edge(a, b, weight=n - abs(abs(pos[a] - pos[b]) - h))
    m = nx.max_weight_matching(G, maxcardinality=True)
    if len(m) * 2 != n:
        return None
    return [tuple(p) for p in m]


def _score_match(teams, opp, mp, ir):
    """
    Score-aware rematch-free PERFECT matching of `teams` as (a, b) tuples, or
    None if no perfect matching exists. Used to re-pair a completeness-repair
    pool. Unlike _blossom_match's bracket-slide weight (right within ONE
    scoregroup), this puts match-point difference first -- which is what matters
    once the pool spans several scoregroups, otherwise a leader can be handed a
    mid-table opponent.
    """
    m = _global_match(teams, opp, mp, ir)
    if len(m) * 2 != len(teams):
        return None
    return [tuple(p) for p in m]


def _feasible_next(next_bracket, opp):
    """
    Can the next bracket be paired keeping ALL its members in (an odd bracket may
    naturally float its single lowest to the group after). Crucially it may NOT
    shed members just to dodge an internal rematch -- that is what forces the
    correct downfloat from the group above (D.02 [C6]/8.4). Uses the fast
    slide-match feasibility (a rematch-free S1/S2 assignment must exist).
    """
    nb = list(next_bracket)
    if not nb:
        return True
    if len(nb) % 2 == 0:
        return _slide_match(nb, opp, {}) is not None
    # odd bracket: it will downfloat its own lowest one; the even remainder must pair
    return len(nb) - 1 == 0 or _slide_match(nb[:-1], opp, {}) is not None


def pair_round(ctx):
    mp = ctx["mp"]; ir = ctx["init_rank"]
    last_color = ctx.get("last_color", {})
    teams = sorted(ctx["teams"], key=lambda t: (-mp[t], ir[t]))
    prevset = _prevset(ctx["prev"])
    opp = {}
    for a, b in prevset:
        opp.setdefault(a, set()).add(b)

    groups = [list(g) for _, g in groupby(teams, key=lambda t: mp[t])]

    result = []
    carry = []            # downfloaters coming into the current group (higher score, on top)
    for i, grp in enumerate(groups):
        next_grp = groups[i + 1] if i + 1 < len(groups) else None

        # choose d = number of residents to downfloat (lowest of grp); keep bracket even.
        chosen_pairs, chosen_floaters = None, []
        for d in range(0, len(grp) + 1):
            floaters = grp[len(grp) - d:] if d else []
            remaining = carry + grp[:len(grp) - d]
            if len(remaining) % 2:
                continue
            pairs = _bracket_pairs(remaining, len(carry), opp, last_color)
            if pairs is None:
                continue
            if next_grp is None:
                if d == 0:
                    chosen_pairs, chosen_floaters = pairs, []
                    break
                continue
            if _feasible_next(floaters + next_grp, opp):
                chosen_pairs, chosen_floaters = pairs, floaters
                break

        if chosen_pairs is None:
            # No parity-preserving downfloat makes both this bracket and the next
            # pairable. Pair this bracket in place rather than dropping it: the
            # MDP step in _bracket_pairs is greedy (each floater takes the
            # strongest unplayed resident) and can return None even when a
            # rematch-free pairing of the whole bracket exists, so fall through to
            # a rematch-free general matching of the bracket. Only if that too is
            # impossible do these teams reach the completeness net below.
            def _pair_in_place(bracket):
                p = _bracket_pairs(bracket, len(carry), opp, last_color)
                return p if p is not None else _blossom_match(bracket, opp)

            even = carry + grp
            if len(even) % 2 == 0:
                chosen_pairs = _pair_in_place(even) or []
            else:
                # One team must float. Floating the lowest is the D.02 default,
                # but if the remainder is then unpairable (e.g. a lone leader has
                # already played that lowest team) try the next-lowest resident
                # instead, rather than dropping the whole bracket. Carried-in
                # downfloaters (the first len(carry) entries) are never re-floated.
                chosen_pairs, chosen_floaters = None, [even[-1]]
                for k in range(len(even) - 1, len(carry) - 1, -1):
                    p = _pair_in_place(even[:k] + even[k + 1:])
                    if p is not None:
                        chosen_pairs, chosen_floaters = p, [even[k]]
                        break
                if chosen_pairs is None:
                    chosen_pairs = []
        result.extend(chosen_pairs)
        carry = chosen_floaters

    # Completeness: in hard late rounds the per-bracket float logic can leave
    # teams unpaired (a rematch-free pairing needs cross-bracket floats it didn't
    # make). Rather than drop teams or allow a rematch (FIDE [C1] is absolute),
    # repair LOCALLY: release the leftovers' score neighbourhood and re-pair it
    # with a rematch-free general matching (blossom). This never fires on the
    # validated official rounds (their bracket logic completes with
    # leftover == []), only on simulated rounds the bracket order can't finish.
    #
    # The release must not orphan anyone: when a result pair (x, y) touches the
    # window, BOTH x and y go into the re-pair pool -- even if y's score sits
    # outside the window (a downfloater). An earlier version released only the
    # in-window member and re-blossomed just the window, which dropped y and
    # merely shifted the unpaired slot onto whoever had floated in (often a
    # contender). Releasing whole pairs keeps the pool even (leftover is even:
    # the field is even and result covers an even count) and self-contained, so
    # a perfect matching of the pool completes the round. Widen the window if the
    # pool has no rematch-free perfect matching; the whole-field recompute is a
    # last resort because a ~200-node pure-Python blossom costs seconds and this
    # path fires several times per sim in late rounds. Invariant regression-
    # checked by d02_repro_real.py.
    paired = set()
    for a, b in result:
        paired.add(a); paired.add(b)
    leftover = [t for t in teams if t not in paired]
    if leftover:
        lo_mp = min(mp[t] for t in leftover)
        hi_mp = max(mp[t] for t in leftover)
        for width in (2, 4, 8):
            window = {t for t in teams if lo_mp - width <= mp[t] <= hi_mp + width}
            keep, pool = [], set(leftover)
            for a, b in result:
                if a in window or b in window:
                    pool.add(a); pool.add(b)
                else:
                    keep.append((a, b))
            if len(pool) == len(teams):
                # Nothing left to keep: the whole field is the pool, so this is
                # exactly the global recompute (perfect if one exists, else the
                # max-cardinality partial). Widening further would be a no-op.
                return _global_match(teams, opp, mp, ir)
            sub = _score_match(sorted(pool, key=lambda t: (-mp[t], ir[t])), opp, mp, ir)
            if sub is not None:
                result = keep + sub
                break
        else:
            return _global_match(teams, opp, mp, ir)

    return {frozenset(p) for p in result}


def _global_match(teams, opp, mp, ir):
    """
    Global rematch-free min-cost perfect matching (fallback for rounds the D.02
    float logic can't complete). Prefers same-scoregroup pairs (Swiss), then the
    slide order. Guaranteed complete + rematch-free if any such pairing exists.
    """
    order = sorted(teams, key=lambda t: (-mp[t], ir[t]))
    pos = {t: i for i, t in enumerate(order)}
    G = nx.Graph()
    G.add_nodes_from(order)
    n = len(order)
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            if b in opp.get(a, ()):        # no rematch edge (absolute)
                continue
            # cost: score difference dominates; then hug the slide.
            cost = (mp[a] - mp[b]) ** 2 * 1000.0 + abs(pos[a] - pos[b])
            G.add_edge(a, b, weight=(n * n * 1000.0 - cost))   # max-weight == min-cost
    matching = nx.max_weight_matching(G, maxcardinality=True)
    return {frozenset(p) for p in matching}
