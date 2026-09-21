# Olympiad 2026 — Data & DB Schema

Reference for the Pawnalyze website team. It describes every Postgres table the
simulation pipeline (`chessSim/`) writes for the **46th Chess Olympiad,
Samarkand 2026** (Open + Women's), the conventions they follow, and the queries
the site is expected to run. The pipeline that produces all of this:

| Step | Script | Output |
|------|--------|--------|
| Scrape teams / players / R1 pairings | `chessSim/scrapeOlympiad.py <open\|women>` | CSVs under `chessSim/data/olympiad/2026/<event>/` |
| Simulate + upload | `chessSim/runOlympiadSims.py <open\|women> --sims 10000 --upload` | all tables below |
| Per-round update (scrape + games + re-sim, sets current) | `chessSim/updateOlympiadRound.py <open\|women>` — run automatically by the cron poller `pollOlympiad.py` | all tables below |
| **Regenerate a historical round** (non-current run) | `chessSim/runOlympiadSims.py <open\|women> --sims 10000 --upload --through-round N` (N=0 is pre-tournament); `chessSim/backfill_olympiad.sh` does every round | `runs`/`sims`/`team_summary` |
| DB access layer (DDL + upserts) | `chessSim/olympiadDB.py` | — |

**Invariant:** every `(event, rounds_completed)` from 0 up to the current round has
**exactly one** `pipeline` run, and every pipeline run has a full `team_summary`.
The pipeline enforces this on each upload: a re-run of a round replaces the prior
run for that round, and a run row with no `team_summary` (a crashed upload) is
deleted rather than allowed to shadow a real run.

Credentials come from the repo-root `.env` (`POSTGRES_*`); see `.env.example`.
The DDL in `olympiadDB.py` is the source of truth and is applied idempotently on
every run — this doc mirrors it.

---

## Conventions (read first)

- **Two events** share one set of tables, distinguished by an `event` column:
  `'open'` | `'women'`.
- **`team_id` = the chess-results starting number (snr)**, 1-based and contiguous
  over *all registered teams* (Open: 1..206, Women: 1..189). It is the stable
  key everywhere. **Do not key on `fed_code`** — federations repeat (Uzbekistan
  2 and 3 both `UZB`). The entry list settled a few days before R1; earlier
  scrapes saw 207/191 and the trailing ids shifted. `*_teams` is now pruned to
  the current entry list on every update, and a run whose `n_teams` differs
  from the previous run carries a `notes` line (`n_teams changed A -> B`).
- **Participants = every team in any published pairing.** A team is simulated
  if it appears in *any* round's team-vs-team pairing (completed or scheduled).
  This includes the late-arriving delegations that were "not paired" in Round 1
  and joined from R2 (Angola, Côte d'Ivoire, Central African Republic, and
  Marshall Islands in the Open) — from **21 Sep** these are in every run
  (Open 206 / Women 189 participants); runs before that had 202 / 186 and are
  being regenerated. A team never given a real pairing is excluded: it carries
  **0** in every array and gets no `team_summary` row. A round a team did not
  play (absent, or a bye) is 0 in `round_opps`; a **bye** carries 4 half-points
  in `round_scores` and 1 MP (FIDE Regs 4.1/4.3 — verified against the
  chess-results ranking table), an **absent** team carries 0. A team that
  **withdraws** mid-event (stops appearing in the published pairings) keeps its
  results to date and is ranked, but is not paired in simulated rounds.
- **Scores are half-points.** A board is worth 2 (win) / 1 (draw) / 0. A 4-board
  match totals **0..8** half-points; **4 = a drawn match**. So "team wins a
  match" ⇔ score `> 4`, "draw" ⇔ `= 4`, "loss" ⇔ `< 4`. Match points (MP) are
  separate: **2** for a match win, **1** for a drawn match, **0** for a loss.
- **Arrays are Postgres 1-based and indexed by `team_id`.** `final_rank[t]` is
  team `t`'s finish; `round_scores[r][t]` is team `t`'s half-point score in round
  `r` (`r` = 1..11). Array length = `n_teams` (206 / 189). A team that did not
  play a given round has 0 there.
- **11 rounds**, Swiss, both events. Ranking is **Match Points**, then tiebreaks
  (FIDE Olympiad 2026 Regs, Appendix 2.I): **IS(10)** Olympiad Sonneborn-Berger
  Cut-1 → **Game Points** → **sum of opponents' MP** Cut-1. The engine's
  `final_rank` already applies these; the site's *live* standings during the
  event should come from the official `*_standings`/chess-results, not the sim.

---

## Reference tables (upserted from chess-results each run)

### `olympiad_2026_teams`
One row per registered team.

| column | type | notes |
|--------|------|-------|
| `event` | text | `'open'`/`'women'` |
| `team_id` | smallint | snr; PK part |
| `fed_code` | text | 3-letter FED (e.g. `USA`) — for display/flag only |
| `name` | text | e.g. `United States of America` |
| `avg_rating` | smallint | chess-results RtgAvg |
| `captain` | text | nullable |

PK `(event, team_id)`.

### `olympiad_2026_players`
Rosters (boards 1..5, incl. reserve).

| column | type | notes |
|--------|------|-------|
| `event` | text | |
| `team_id` | smallint | FK → teams |
| `board` | smallint | 1..6 |
| `name` | text | `Caruana, Fabiano` |
| `title` | text | `GM`/`IM`/… nullable |
| `rating` | smallint | |
| `fide_id` | integer | nullable |

PK `(event, team_id, board)`, FK `(event, team_id)` → teams (cascade).

### `olympiad_2026_matches`
Team pairings/results per round. Pre-tournament this holds the official Round-1
pairings with `status='scheduled'` and NULL scores; the pipeline updates it as
rounds are played.

| column | type | notes |
|--------|------|-------|
| `event` | text | |
| `round` | smallint | 1..11 |
| `board_no` | smallint | pairing/table number within the round (PK part) |
| `team1_id` | smallint | board-1 **white** team |
| `team2_id` | smallint | **NULL = pairing-allocated bye** (odd field); `team1_score` is then 4 (the bye's 2 GP) once the round is underway, `status` `scheduled` before |
| `team1_score` | smallint | half-points 0..8, NULL until known |
| `team2_score` | smallint | half-points 0..8, NULL until known |
| `status` | text | `scheduled` \| `live` \| `final` |
| `updated_at` | timestamptz | |

PK `(event, round, board_no)`; index on `(event, round, status)`.

---

## Simulation tables

### `olympiad_2026_runs`
One row per Monte-Carlo run. A run is a snapshot: "N sims given the first
`rounds_completed` rounds fixed to their real results."

| column | type | notes |
|--------|------|-------|
| `run_id` | serial | PK |
| `event` | text | |
| `rounds_completed` | smallint | 0 = pre-tournament, up to 11 |
| `n_sims` | integer | e.g. 10000 |
| `n_teams` | smallint | array length (206 / 189) |
| `source` | text | `pipeline` \| `synthetic` (local seed data) |
| `is_current` | boolean | exactly one true per event |
| `created_at` | timestamptz | |
| `notes` | text | nullable; set when `n_teams` changes vs the previous run, and `backfill through RN` on a regenerated historical run |

Partial unique index guarantees a single `is_current` run per event
(`... WHERE is_current`); history index on `(event, rounds_completed, created_at DESC)`.
**Always resolve the current run first**, then query `sims`/`team_summary` by its
`run_id`. The pipeline flips `is_current` atomically after a successful upload.

### `olympiad_2026_sims`
The raw per-simulation results — the substrate for the scenario explorer. One
row per simulated tournament.

| column | type | notes |
|--------|------|-------|
| `run_id` | integer | FK → runs (cascade) |
| `sim_id` | integer | 0..n_sims-1 |
| `gold` `silver` `bronze` | smallint | `team_id`s of the final top 3 |
| `top10` | smallint[] | `team_id`s at final ranks 1..10, **in order** |
| `final_rank` | smallint[] | `final_rank[team_id]` = 1..n_teams (0 = did not play) |
| `match_points` | smallint[] | `match_points[team_id]`, 0..22 |
| `game_points` | smallint[] | `game_points[team_id]` in **half-points**, 0..88 |
| `round_scores` | smallint[] (2-D) | `round_scores[round][team_id]` in half-points, 0..8 |
| `round_opps` | smallint[] (2-D) | `round_opps[round][team_id]` = that team's opponent team_id; 0 = bye, -1 = did not play; non-participants 0 everywhere |

PK `(run_id, sim_id)`. `round_scores` and `round_opps` are rectangular
`11 × n_teams` arrays (1-based, same indexing). `round_opps` lets the site show
pairing odds for future rounds: completed rounds hold the real pairings, the next
round holds the official published pairings (fixed across sims), and later rounds
hold the simulated Swiss pairings (vary per sim). Symmetry holds
(`round_opps[r][round_opps[r][t]] == t`), and for opp>0
`round_scores[r][t] + round_scores[r][opp] == 8` **except** real completed rounds,
which can total <8 when a board is forfeited/unplayed.

**Scenario predicates are array subscripts.** "IND (team_id 2) beats USA (1) in
round 5" ⇒ `round_scores[5][2] > 4`. "GEO (team_id 3) wins round 8" (unknown
future pairing) ⇒ `round_scores[8][3] > 4`. Draw ⇒ `= 4`, loss ⇒ `< 4`. The same
subscript shape covers both known next-round pairings and unknown future rounds.

### `olympiad_2026_team_summary`
Pre-aggregated per-team probabilities for one run (so the default page needs no
heavy aggregation). One row per **participating** team.

| column | type | notes |
|--------|------|-------|
| `run_id` | integer | FK → runs (cascade) |
| `event` | text | |
| `team_id` | smallint | |
| `p_gold` `p_silver` `p_bronze` | real | probability 0..1 |
| `p_medal` | real | `p_gold + p_silver + p_bronze` |
| `p_top10` | real | 0..1 |
| `exp_rank` | real | mean final rank |
| `exp_mp` | real | mean match points (0..22) |
| `exp_gp` | real | mean **board** game points (0..44) — note: NOT half-points |

PK `(run_id, team_id)`. `sum(p_gold)` over a run ≈ 1.0 (sanity check).

---

## Example queries

Resolve the current run:
```sql
SELECT run_id, rounds_completed, n_sims, n_teams
FROM olympiad_2026_runs WHERE event = 'open' AND is_current;
```

Default medal board (no scenario) — just read the summary:
```sql
SELECT ts.team_id, t.name, t.fed_code,
       ts.p_gold, ts.p_silver, ts.p_bronze, ts.p_medal, ts.p_top10, ts.exp_rank
FROM olympiad_2026_team_summary ts
JOIN olympiad_2026_teams t ON t.event = ts.event AND t.team_id = ts.team_id
WHERE ts.run_id = $1
ORDER BY ts.p_medal DESC;
```

Scenario ("IND wins R5 and R8") — recompute medal/rank odds over matching sims:
```sql
WITH m AS (
  SELECT top10, final_rank FROM olympiad_2026_sims
  WHERE run_id = $1 AND round_scores[5][2] > 4 AND round_scores[8][2] > 4)
SELECT (SELECT count(*) FROM m) AS matched,
       u.team_id, count(*)::int AS n, u.rank
FROM m, unnest(m.top10) WITH ORDINALITY AS u(team_id, rank)
GROUP BY u.team_id, u.rank;
```
`p_gold = n(rank=1)/matched`, `p_medal = Σ ranks 1..3`, `p_top10 = Σ ranks 1..10`.
Prefer `unnest(top10)` (≤10 rows/sim) over unnesting `final_rank` (n_teams rows).
For per-team `exp_rank`/`exp_mp` under a scenario, `unnest(final_rank)` /
`unnest(match_points)` `WITH ORDINALITY` filtered to the picked teams.

Scenario-filter grammar the API validates: tokens `round:team_id:{w|d|l}` →
`round_scores[round][team_id] {>|=|<} 4`; require `round > rounds_completed`,
`1 ≤ round ≤ 11`, `1 ≤ team_id ≤ n_teams`, dedupe, cap (~30).

---

## Cadence & lifecycle

1. **Pre-tournament** (before Sept 16): run with `rounds_completed = 0`.
2. **After each round**: re-scrape (`scrapeOlympiad.py` picks up completed rounds
   automatically) and re-run with `--upload`; `rounds_completed` increments. Every
   sim holds the completed rounds fixed and simulates the rest.
3. Each upload: upsert teams/players/matches → insert `runs` row (`is_current=false`)
   → bulk insert `sims` → insert `team_summary` → flip `is_current` atomically →
   prune old raw sims (summaries kept for history) → ping `REVALIDATE_URL`.
4. **Final** after round 11: `rounds_completed = 11`, every sim is the actual result.

### Sim retention (storage)
All runs keep up to **10k** sims (`past_sims_keep`). The **current** run may be
simulated with MORE than 10k for extra pick-em precision; once it is no longer
current it is trimmed back to 10k. **All runs keep their `runs` row and
`team_summary`**, so the odds-over-time history (which reads `team_summary`, not
raw `sims`) is fully preserved regardless.

## Live-results tables (populated round-by-round)

The per-round updater (`chessSim/updateOlympiadRound.py`, run by the auto-poller
`pollOlympiad.py`) refreshes these after each round. `matches` now carries real
scores + status (not just scheduled R1 pairings).

### `olympiad_2026_matches` (now populated with results)
As documented above, plus: after each round, completed matches have
`status='final'` with `team1_score`/`team2_score` in half-points (0..8), and the
next round's pairings appear with `status='scheduled'` and NULL scores.
`board_no` is the chess-results table/pairing number.

### `olympiad_2026_games` — individual board games (with moves)
Board-level games, sourced from the **Lichess broadcast** (primary; chess.com
backup), reconciled to a team match by FIDE id.

| column | type | notes |
|--------|------|-------|
| `event` | text | |
| `round` | smallint | 1..11 |
| `board_no` | smallint | team-match number (FK → `matches`) |
| `board` | smallint | 1..4 within the match |
| `white_team_id` `black_team_id` | smallint | resolved via FIDE id (nullable if unresolved) |
| `white_player` `black_player` | text | |
| `white_fide_id` `black_fide_id` | integer | |
| `white_elo` `black_elo` | smallint | |
| `result` | text | `1-0` / `1/2-1/2` / `0-1` / `*` (in progress) |
| `pgn` | text | moves for the game viewer (no clocks/evals) |
| `source` | text | `lichess` / `chesscom` / `chess-results` |
| `updated_at` | timestamptz | |

PK `(event, round, board_no, board)`; FK `(event, round, board_no)` → `matches`
(cascade); index on `(white_fide_id, black_fide_id)`. Live games appear with
`result='*'` and update to a final result as they finish.

### `olympiad_2026_standings` — official team standings after every completed round
One row per team per completed round. **`rank` and the tiebreaks are the official
chess-results values** (its ranking table after round N, which it serves per
round, so past rounds are exact, not reconstructed). `mp` / `gp_hp` are derived
from `matches` and cross-checked against the official values on every scrape (a
mismatch is logged loudly), so a site-side derivation from `matches` agrees
with them exactly — including byes (1 MP / 4 half-points).

Each block is **exactly the official page's team set** for that round: a late
arrival that chess-results already lists before its first pairing is present
at 0 MP / 0 GP with its official rank (chess-results ranks it among the other
0-point teams, so it is not necessarily last), so ranks run 1..n with no gaps.
A team chess-results had not yet added is simply absent from that block (Open
R1–R2 have 205 rows; R3+ have 206). Every scrape rewrites all blocks
1..completed and **replaces** each one — rows keyed by a superseded SNo (from
a chess-results renumbering) are deleted, never left to duplicate a rank.

| column | type | notes |
|--------|------|-------|
| `event` | text | |
| `after_round` | smallint | 1..11 — one block per completed round |
| `team_id` | smallint | |
| `rank` | smallint | **official** chess-results rank, 1 = leader. (chess-results prints a blank rank on a row that ties the row above on the displayed tiebreaks; the pipeline fills it from the row's position, which is exact.) |
| `mp` | smallint | match points (= official TB1) |
| `gp_hp` | smallint | game points in half-points (= official TB3 × 2) |
| `tb1` | real | official **TB2 — Olympiad Sonneborn-Berger without lowest result ("Chennai")**: the first tiebreak after match points |
| `tb2` | real | official **TB3 — game points** (= `gp_hp / 2`) |
| `tb3` | real | official **TB4 — Olympiad sum of adjusted match points without lowest result ("Chennai")** |
| `updated_at` | timestamptz | |

PK `(event, after_round, team_id)`. Ranking order is `mp` desc → `tb1` desc →
`tb2` desc → `tb3` desc, which is what `rank` encodes. If chess-results' ranking
page for a round is ever unavailable, that round falls back to a derived rank
(by `mp`, `gp_hp`) with `tb*` NULL rather than failing the update.

> Read `rank` from this table for completed rounds. Use the **simulation's**
> `final_rank` only for projected/what-if standings.
