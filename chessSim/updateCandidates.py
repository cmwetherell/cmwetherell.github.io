import pandas as pd
from multiprocessing import Pool
from itertools import repeat
from sqlalchemy import create_engine, text
import time
from tqdm import tqdm
import time
from multiprocessing import set_start_method
# import json
from dotenv import load_dotenv
import os

# Scraper imports are conditional on --no-scrape flag (see __main__ block)

load_dotenv()

# PostgreSQL connection details
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')

def detect_round(games_csv: pd.DataFrame) -> str:
    """Detect the current round from the games CSV.

    Counts round-robin games with played=1 and divides by 4
    (4 games per round with 8 players). Returns 'Pre' if no
    games have been played, otherwise the round number as a string.
    """
    rr_games = games_csv[games_csv['stage'] == 'rr']
    played = int(rr_games['played'].sum())
    if played == 0:
        return "Pre"
    return str(played // 4)


def convert_to_df(data, rnd):
    # Initialize an empty list to hold each simulation's data
    all_simulations = []

    # Iterate over each simulation in the loaded data
    for simulation in data:
        # Initialize a dictionary for the current simulation
        simulation_dict = {
            'winner': simulation['winner'],
            'second': simulation['second'],
            'tie': simulation['tie']
        }
        
        # Iterate over the games in the current simulation
        for game in simulation['games']:
            # Use the gameId as the key and the outcome as the value
            simulation_dict[game['gameId']] = game['outcome']
        
        # Append the current simulation's data to the list
        all_simulations.append(simulation_dict)

    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(all_simulations)

    # If there are missing values (games not present in every simulation), fill them with a default value, e.g., NaN or 0
    df.fillna(value=0, inplace=True)

    # Downcast game columns from float64 (8 bytes) to float32 (4 bytes) to halve storage.
    # Values 0.0, 0.5, 1.0 are exactly representable in float32.
    game_cols = [c for c in df.columns if '|' in c]
    df[game_cols] = df[game_cols].astype('float32')

    df['Round'] = rnd

    return df

def main(nsims: int, tourn: str, rnd: int | str):

    start_time = time.time()

    if tourn == "open":
        from utils import simCandidatesTournament as simCand
        current = pd.read_csv("./chessSim/data/candidatesGames2026.csv")
        table_name = 'candidates_2026'
    elif tourn == "womens":
        print("running womens")
        from utils import simWomensCandidatesTournament as simCand
        current = pd.read_csv("./chessSim/data/womensCandidatesGames2026.csv")
        table_name = 'womens_candidates_2026'
    else:
        raise ValueError("Invalid tournament name")

    with Pool() as p:
            # Use imap_unordered for potentially faster execution since the order of results may not matter
            # Wrap the repeat iterable with tqdm to show progress, specifying the total number of tasks
            results = list(tqdm(p.imap_unordered(simCand, repeat(current, nsims)), total=nsims, desc="Simulating"))

    winners, seconds, ties, simulation_results = zip(*results)

    # Compress and save to a gzip file
    # with gzip.open(f'./chessSim/data/sims/candidates_{"" if tourn == "open" else "womens"}_results.json.gz', 'wt', encoding='UTF-8') as file:
    #     json.dump(simulation_results, file)
        
    print("--- %s seconds ---" % (time.time() - start_time))
    # print time per nSim in seconds
    print((time.time() - start_time)/nsims)

    # # Create a DataFrame from the simulation results
    df = convert_to_df(simulation_results, rnd)

    # # Create the SQLAlchemy engine
    engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}?sslmode=require')

    df.to_sql(table_name, con=engine, if_exists='append', index=False, chunksize=1000)

    # Create index on Round for faster filtered queries (idempotent)
    with engine.connect() as conn:
        idx_name = f'idx_{table_name}_round'
        conn.execute(text(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ("Round")'))
        conn.commit()

    print(f"DataFrame uploaded successfully to {table_name} table.")

if __name__=="__main__":
    set_start_method("spawn")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", required=False, default=None,
        help="Which round to simulate (auto-detected from CSV if omitted)")
    parser.add_argument("--nsims", type=int, default=1000, help="Number of simulations to run")
    parser.add_argument("--tourn", type=str, default="open", help="Which tournament to run")
    parser.add_argument("--ratings", type=str, default="fide", choices=["fide", "2700chess", "cached"],
        help="Rating source: fide (official FIDE download, default), 2700chess (live scrape), cached (existing pickle files)")
    args = parser.parse_args()

    if args.ratings == "fide":
        import scrape_fide
    elif args.ratings == "2700chess":
        # FIDE first (baseline for all players), then 2700chess overlays live ratings
        import scrape_fide
        import scrape2700
        import scrape2700women

    # Auto-detect round from CSV if not explicitly provided
    if args.round is not None:
        rnd = args.round
    else:
        tourns = ["open", "womens"] if args.tourn == "both" else [args.tourn]
        csv_paths = {
            "open": "./chessSim/data/candidatesGames2026.csv",
            "womens": "./chessSim/data/womensCandidatesGames2026.csv",
        }
        detected = {t: detect_round(pd.read_csv(csv_paths[t])) for t in tourns}
        for t, r in detected.items():
            print(f"Auto-detected round for {t}: {r}")
        # Use detected round per tournament (they may differ)
        rnd = detected

    for i in range (0, args.nsims // 10000):
        print(f"Running simulation {i}...")
        nsims = min(args.nsims, 10000)

        if args.tourn =="both":
            r_open = rnd if isinstance(rnd, str) else rnd["open"]
            r_womens = rnd if isinstance(rnd, str) else rnd["womens"]
            main(nsims=nsims, tourn="open", rnd=r_open)
            main(nsims=nsims, tourn="womens", rnd=r_womens)
        else:
            r = rnd if isinstance(rnd, str) else rnd[args.tourn]
            main(nsims=nsims, tourn=args.tourn, rnd=r)
