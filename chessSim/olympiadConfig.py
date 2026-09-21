"""
Configuration for Chess Olympiad simulations.

One pipeline drives both the Open and Women's events (and future years):
scrapeOlympiad.py, simOlympiad.py and runOlympiadSims.py all read an
EventConfig from here rather than hardcoding a tournament id / year.

Regulations reference (46th Chess Olympiad, Samarkand 2026):
  - FIDE Olympiad 2026 Main Competition Regulations:
    https://handbook.fide.com/files/handbook/Olympiad2026MainCompetition.pdf
  - FIDE Olympiad Pairing Rules (D.02, 2022, still governing for 2026):
    https://handbook.fide.com/chapter/OlympiadPairingRules2022

  Both sections: Swiss system, 11 rounds.
  Ranking: Match Points (win 2 / draw 1 / loss 0), then tiebreaks (Appendix 2.I):
    TB1  IS(10)  - Olympiad Sonneborn-Berger, Cut-1 (sum of ISi over the 10 best
                   opponents, dropping the bye round or the lowest-MP opponent).
                   ISi = (game points vs opp i) * (opp i's final match points).
    TB2  GP      - total game points.
    TB3  MP(10)  - sum of the match points of opponents, Cut-1.
  Bye (odd number of teams): lowest-ranked eligible team; awarded 1 MP + 2 GP.
"""

import os
from dataclasses import dataclass, field


# chessSim/ directory, used to build absolute-ish data paths that work whether
# the script is launched from the repo root or from chessSim/.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_ROOT = os.path.join(_THIS_DIR, "data", "olympiad")


# All simulation + reference data live in shared, event-tagged tables (an
# `event` column of 'open' | 'women') rather than per-event tables, so the
# website's query layer reads one schema. See SCHEMA.md for the DDL.
TABLE_PREFIX = "olympiad_2026"
TEAMS_TABLE = f"{TABLE_PREFIX}_teams"
PLAYERS_TABLE = f"{TABLE_PREFIX}_players"
MATCHES_TABLE = f"{TABLE_PREFIX}_matches"
RUNS_TABLE = f"{TABLE_PREFIX}_runs"
SIMS_TABLE = f"{TABLE_PREFIX}_sims"
TEAM_SUMMARY_TABLE = f"{TABLE_PREFIX}_team_summary"
GAMES_TABLE = f"{TABLE_PREFIX}_games"
STANDINGS_TABLE = f"{TABLE_PREFIX}_standings"

# Sentinel opponent name for a pairing-allocated bye in matches.csv /
# round_results.csv (team2 == BYE). A bye scores 1 MP + BYE_GP game points
# (FIDE Olympiad Regs 4.1/4.3; verified against the chess-results ranking
# table). Shared by the scraper and the simulator.
BYE = "bye"
BYE_GP = 2.0


@dataclass(frozen=True)
class EventConfig:
    key: str                # 'open' or 'women'
    tnr: int                # chess-results tournament id
    year: int
    label: str              # human-readable, e.g. "Open"
    n_rounds: int = 11
    server: str = "s1"      # chess-results mirror (s1/s2/s3)
    # Substring that identifies this event's Lichess broadcast tournaments. Lichess
    # splits the ~400 games/round across several overlapping feeds ("... | I",
    # "... | II", ...); we search by this substring and union all matching feeds.
    lichess_broadcast_match: str = ""
    chesscom_event_slug: str = ""   # best-effort chess.com backup (optional)

    @property
    def data_dir(self) -> str:
        return os.path.join(_DATA_ROOT, str(self.year), self.key)

    @property
    def base_url(self) -> str:
        return f"https://{self.server}.chess-results.com/tnr{self.tnr}.aspx"

    def url(self, **params) -> str:
        params.setdefault("lan", 1)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}?{query}"

    # --- file paths (all under data_dir) ---
    def path(self, name: str) -> str:
        return os.path.join(self.data_dir, name)

    @property
    def players_csv(self) -> str:
        return self.path("players.csv")

    @property
    def teams_csv(self) -> str:
        return self.path("teams.csv")

    @property
    def matches_csv(self) -> str:
        """Completed team-match results (empty pre-tournament)."""
        return self.path("matches.csv")

    @property
    def round1_pairings_csv(self) -> str:
        """Official round-1 pairings published by chess-results."""
        return self.path("round1_pairings.csv")

    @property
    def team_map_json(self) -> str:
        return self.path("team_map.json")

    @property
    def round_results_csv(self) -> str:
        """Per-match team results with board_no + status, for the DB matches table."""
        return self.path("round_results.csv")

    @property
    def standings_csv(self) -> str:
        return self.path("standings.csv")

    @property
    def games_csv(self) -> str:
        """Reconciled board-level games (from Lichess/chess.com)."""
        return self.path("games.csv")


EVENTS = {
    "open": EventConfig(
        key="open", tnr=1469895, year=2026, label="Open",
        lichess_broadcast_match="Samarkand 2026 | Open",
    ),
    "women": EventConfig(
        key="women", tnr=1469896, year=2026, label="Women's",
        lichess_broadcast_match="Samarkand 2026 | Women",
    ),
}


def get_event(key: str) -> EventConfig:
    key = key.lower().strip()
    if key in ("w", "women", "womens", "women's"):
        key = "women"
    if key in ("o", "open"):
        key = "open"
    if key not in EVENTS:
        raise SystemExit(
            f"Unknown event '{key}'. Choose one of: {', '.join(EVENTS)}"
        )
    return EVENTS[key]
