"""
Rebuild historical simulation data: 10k sims per round (Pre through R6)
for both Open and Women's Candidates 2026.
"""

import json
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chessSim.updateCandidates import main as run_sims

OPEN_CSV = "./chessSim/data/candidatesGames2026.csv"
WOMENS_CSV = "./chessSim/data/womensCandidatesGames2026.csv"
OPEN_JSON = "./chessSim/data/candResByRound2026.json"
WOMENS_JSON = "./chessSim/data/womensCandByRound2026.json"
OPEN_BACKUP = "./chessSim/data/candidatesGames2026_R6_backup.csv"
WOMENS_BACKUP = "./chessSim/data/womensCandidatesGames2026_R6_backup.csv"

# Map JSON game IDs to full player names
OPEN_PLAYERS = {
    'Nak': 'Nakamura, Hikaru',
    'Car': 'Caruana, Fabiano',
    'Gir': 'Giri, Anish',
    'Pra': 'Praggnanandhaa R',
    'Wei': 'Wei, Yi',
    'Sin': 'Sindarov, Javokhir',
    'Esi': 'Esipenko, Andrey',
    'Blu': 'Bluebaum, Matthias',
}

WOMENS_PLAYERS = {
    'Muz': 'Muzychuk, Anna',
    'Gor': 'Goryachkina, Aleksandra',
    'Lag': 'Lagno, Kateryna',
    'Ass': 'Assaubayeva, Bibisara',
    'Ram': 'Rameshbabu, Vaishali',
    'Des': 'Deshmukh, Divya',
    'Tan': 'Tan, Zhongyi',
    'Zhu': 'Zhu, Jiner',
}

OUTCOME_MAP = {'white': 1.0, 'draw': 0.5, 'black': 0.0}


def build_csv_for_round(backup_csv_path, json_path, player_map, target_round, output_csv_path):
    """Build a CSV with games played through `target_round` (0 = Pre, no games played)."""
    df = pd.read_csv(backup_csv_path)

    # Reset all games to unplayed
    df['played'] = 0
    df['result'] = 0.0

    if target_round == 0:
        df.to_csv(output_csv_path, index=False)
        return

    with open(json_path) as f:
        rounds_data = json.load(f)

    for rnd_data in rounds_data:
        rnd_num = rnd_data['round']
        if rnd_num > target_round:
            break
        for game in rnd_data['games']:
            if 'outcome' not in game:
                continue  # Future round, no result yet
            game_id = game['id']
            white_code, black_code = game_id.split('|')
            white_name = player_map[white_code]
            black_name = player_map[black_code]
            result = OUTCOME_MAP[game['outcome']]

            mask = (df['whitePlayer'] == white_name) & (df['blackPlayer'] == black_name)
            df.loc[mask, 'played'] = 1
            df.loc[mask, 'result'] = result

    df.to_csv(output_csv_path, index=False)


def rebuild_tournament(tourn, backup_csv, csv_path, json_path, player_map, rounds_to_rebuild):
    """Rebuild sims for specified rounds of one tournament."""
    for rnd in rounds_to_rebuild:
        rnd_label = "Pre" if rnd == 0 else str(rnd)
        print(f"\n{'='*60}")
        print(f"  {tourn.upper()} — Round {rnd_label}: building CSV and running 10k sims")
        print(f"{'='*60}")

        build_csv_for_round(backup_csv, json_path, player_map, rnd, csv_path)

        # Verify played count
        check = pd.read_csv(csv_path)
        played_count = int(check['played'].sum())
        expected = rnd * 4
        print(f"  CSV has {played_count} played games (expected {expected})")
        assert played_count == expected, f"Mismatch! {played_count} != {expected}"

        run_sims(nsims=10000, tourn=tourn, rnd=rnd_label)
        print(f"  Round {rnd_label} complete.")


if __name__ == "__main__":
    from multiprocessing import set_start_method
    set_start_method("spawn")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tourn", type=str, required=True, choices=["open", "womens"],
                        help="Which tournament to rebuild")
    parser.add_argument("--rounds", type=str, default="0,1,2,3,4,5,6",
                        help="Comma-separated round numbers to rebuild (0=Pre)")
    args = parser.parse_args()

    rounds_to_rebuild = [int(r) for r in args.rounds.split(",")]

    if args.tourn == "open":
        rebuild_tournament("open", OPEN_BACKUP, OPEN_CSV, OPEN_JSON, OPEN_PLAYERS, rounds_to_rebuild)
    else:
        rebuild_tournament("womens", WOMENS_BACKUP, WOMENS_CSV, WOMENS_JSON, WOMENS_PLAYERS, rounds_to_rebuild)

    # Restore backup
    if args.tourn == "open":
        os.system(f"cp {OPEN_BACKUP} {OPEN_CSV}")
    else:
        os.system(f"cp {WOMENS_BACKUP} {WOMENS_CSV}")

    print(f"\n✓ All done for {args.tourn}. CSV restored to R6 state.")
