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
            # fallback: pair whatever we can, float the rest (should be rare)
            even = carry + grp
            if len(even) % 2:
                chosen_floaters = [even[-1]]
                even = even[:-1]
            chosen_pairs = _bracket_pairs(even, len(carry), opp, last_color) or []
        result.extend(chosen_pairs)
        carry = chosen_floaters

    # Completeness: in hard late rounds the per-bracket float logic can leave
    # teams unpaired (a rematch-free pairing needs floats it didn't make). Rather
    # than drop teams or allow a rematch (FIDE [C1] is absolute), fall back to a
    # GLOBAL rematch-free min-cost matching for the whole round -- guaranteed
    # complete and rematch-free (blossom), minimising score differences (Swiss).
    paired = set()
    for a, b in result:
        paired.add(a); paired.add(b)
    leftover = [t for t in teams if t not in paired]
    if leftover:
        # Almost always the few leftovers pair among themselves rematch-free
        # (tiny blossom). If they can't, they only need to swap with teams in their
        # own score neighbourhood -- release those pairs and re-blossom that local
        # subset (fast). Whole-field is an ultra-rare last resort.
        leftover.sort(key=lambda t: (-mp[t], ir[t]))
        extra = _blossom_match(leftover, opp)
        if extra is not None:
            result.extend(extra)
        else:
            lo_scores = [mp[t] for t in leftover]
            lo, hi = min(lo_scores) - 2, max(lo_scores) + 2
            subset = sorted((t for t in teams if lo <= mp[t] <= hi),
                            key=lambda t: (-mp[t], ir[t]))
            sset = set(subset)
            result = [(a, b) for a, b in result if a not in sset and b not in sset]
            sub = _blossom_match(subset, opp)
            if sub is None:
                return _global_match(teams, opp, mp, ir)
            result.extend(sub)

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
