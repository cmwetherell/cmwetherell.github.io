# Olympiad 2026 — Data & DB Schema

Reference for the Pawnalyze website team. It describes every Postgres table the
simulation pipeline (`chessSim/`) writes for the **46th Chess Olympiad,
Samarkand 2026** (Open + Women's), the conventions they follow, and the queries
the site is expected to run. The pipeline that produces all of this:

| Step | Script | Output |
|------|--------|--------|
| Scrape teams / players / R1 pairings | `chessSim/scrapeOlympiad.py <open\|women>` | CSVs under `chessSim/data/olympiad/2026/<event>/` |
| Simulate + upload | `chessSim/runOlympiadSims.py <open\|women> --sims 10000 --upload` | all tables below |
| DB access layer (DDL + upserts) | `chessSim/olympiadDB.py` | — |

Credentials come from the repo-root `.env` (`POSTGRES_*`); see `.env.example`.
The DDL in `olympiadDB.py` is the source of truth and is applied idempotently on
every run — this doc mirrors it.

---

## Conventions (read first)

- **Two events** share one set of tables, distinguished by an `event` column:
  `'open'` | `'women'`.
- **`team_id` = the chess-results starting number (snr)**, 1-based and contiguous
  over *all registered teams* (Open: 1..207, Women: 1..191). It is the stable
  key everywhere. **Do not key on `fed_code`** — federations repeat (Uzbekistan
  2 and 3 both `UZB`).
- **Participants vs. registered.** ~5 registered teams per event are "not paired"
  in Round 1 (withdrawn/no-show), so the field that actually plays is **202
  (Open)** / **186 (Women)**. Non-participating `team_id`s still exist in
  `*_teams` but carry **0** in every simulation array and get **no**
  `team_summary` row. Filter them out by `final_rank > 0` / their absence from
  `team_summary`.
- **Scores are half-points.** A board is worth 2 (win) / 1 (draw) / 0. A 4-board
  match totals **0..8** half-points; **4 = a drawn match**. So "team wins a
  match" ⇔ score `> 4`, "draw" ⇔ `= 4`, "loss" ⇔ `< 4`. Match points (MP) are
  separate: **2** for a match win, **1** for a drawn match, **0** for a loss.
- **Arrays are Postgres 1-based and indexed by `team_id`.** `final_rank[t]` is
  team `t`'s finish; `round_scores[r][t]` is team `t`'s half-point score in round
  `r` (`r` = 1..11). Array length = `n_teams` (207 / 191). A team that did not
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
| `team2_id` | smallint | nullable (bye) |
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
| `n_teams` | smallint | array length (207 / 191) |
| `source` | text | `pipeline` \| `synthetic` (local seed data) |
| `is_current` | boolean | exactly one true per event |
| `created_at` | timestamptz | |
| `notes` | text | nullable |

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

PK `(run_id, sim_id)`. `round_scores` is a rectangular `11 × n_teams` array.

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

### `olympiad_2026_standings` — live team standings
Current standings after each completed round, computed from the authoritative
chess-results match scores.

| column | type | notes |
|--------|------|-------|
| `event` | text | |
| `after_round` | smallint | 0..11 |
| `team_id` | smallint | |
| `rank` | smallint | 1 = leader |
| `mp` | smallint | match points |
| `gp_hp` | smallint | game points in half-points |
| `tb1` `tb2` `tb3` | real | official Sonneborn-Berger tiebreaks — **currently NULL**; rank is by (MP, GP). The exact chess-results tiebreak ordering can be layered in from its ranking crosstable once published. |
| `updated_at` | timestamptz | |

PK `(event, after_round, team_id)`.

> For the official champion/medal ranking use the **simulation's** final standings
> once `rounds_completed=11` (it applies the full FIDE Appendix 2.I tiebreaks);
> for mid-event live standings use this table (MP → GP), which matches the public
> leaderboard closely.
