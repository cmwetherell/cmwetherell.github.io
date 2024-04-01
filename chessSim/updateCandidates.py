import pandas as pd
from multiprocessing import Pool
from itertools import repeat
from sqlalchemy import create_engine
import time
from tqdm import tqdm
import time
from multiprocessing import set_start_method
# import json
from dotenv import load_dotenv
import os

from scrape2700 import * #Used to refresh live ratings after a round
from scrape2700women import * #Used to refresh live ratings after a round

load_dotenv()

# PostgreSQL connection details
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')

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

    df['Round'] = rnd

    return df

def main(nsims: int, tourn: str, rnd: int | str, trim: bool = False):
    print(trim, 'trim')
    start_time = time.time()

    if tourn == "open":
        from utils import simCandidatesTournament as simCand
        current = pd.read_csv("./chessSim/data/candidatesGames2024.csv")
        table_name = 'candidates_2024'
    elif tourn == "womens":
        print("running womens")
        from utils import simWomensCandidatesTournament as simCand
        current = pd.read_csv("./chessSim/data/womensCandidatesGames2024.csv")
        table_name = 'womens_candidates_2024'
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
    engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}')

    # # Upload the DataFrame to the '(womens-)candidates-2024' table
    df.to_sql(table_name, con=engine, if_exists='append', index=False)

    print(f"DataFrame uploaded successfully to {table_name} table.")

    if trim: # havent tested this code yet, should try to run some test before deleting all my sims!
        rounds_to_trim = ["Pre"] + list(range(1, rnd))
        for i in rounds_to_trim:
            with engine.connect() as connection:
                print("Trimming round", i)
                # need tp modify to keep sample of 10k records
                # connection.execute(f"DELETE FROM {table_name} WHERE \"Round\" = {i}")

if __name__=="__main__":
    set_start_method("spawn")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", required=True, help="Which round to simulate")
    parser.add_argument("--nsims", type=int, default=1000, help="Number of simulations to run")
    parser.add_argument("--tourn", type=str, default="open", help="Which tournament to run")
    parser.add_argument("--trim", action='store_true', help="Whether to trim the results of old rounds")
    args = parser.parse_args()

    main(nsims=args.nsims, tourn=args.tourn, rnd=args.round, trim=args.trim)
