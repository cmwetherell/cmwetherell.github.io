from re import I
import pandas as pd
from utils import summarizeCurrent
from multiprocessing import Pool
from itertools import repeat
import time
import sys
import pickle
from tqdm import tqdm
from collections import Counter
from multiprocessing import set_start_method
import lightgbm as lgb
import json
import gzip
from utils import upload_dataframe_to_db 
from simOlympiad import main as simOlympiad

def run_simulation_with_timeout(simulation_function, args, timeout_duration):
    """Run a simulation function with a timeout."""
    with Pool(processes=8) as pool:  # Use 8 processes for parallel execution
        results = []
        for result in tqdm(pool.imap_unordered(simulation_function, args), total=len(args), desc="Simulating"):
            results.append(result)
        return results

def simulation_worker(_):
    """Wrapper function to run each simulation."""
    try:
        return simOlympiad(0)
    except Exception as e:
        print(f"Simulation error: {e}")
        return None

def main():
    start_time = time.time()
    terminalArgs = sys.argv

    nSims = 80
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    timeout_duration = 30  # Set the timeout duration in seconds

    # Create a list of tasks
    tasks = repeat(0, nSims)

    # Initialize a multiprocessing pool and execute simulations in parallel with timeouts
    with Pool(processes=8) as pool:  # Use 8 processes for parallel execution
        results = []
        for result in tqdm(pool.imap_unordered(simulation_worker, tasks), total=nSims, desc="Simulating"):
            results.append(result)

    print("--- %s seconds ---" % (time.time() - start_time))
    
    # Process results as you have in the rest of your script
    winsByRound = [results]
    print('dumping')
    pickle.dump(winsByRound, open("./chessSim/data/sims/olympiad45.p", "wb"))
    print('done dumping')

    # Convert results to DataFrame
    df = pd.DataFrame(winsByRound[0])
    df.columns = ['gold', 'silver', 'bronze']
    df['round'] = 'Pre'
    df['future_results'] = ""

    # Upload DataFrame to database
    table_name = 'olympiad_2024'
    upload_dataframe_to_db(table_name, df)
    print("DataFrame uploaded to the database successfully.")

    # Analyze and print simulation results
    ct = Counter([x[0] for x in results if x is not None])
    for key in ct:
        ct[key] /= (nSims / 100)
    print('winners results', ct)

    print("--- %s seconds ---" % (time.time() - start_time))
    print((time.time() - start_time)/nSims)

    
if __name__=="__main__":
    set_start_method("spawn")
    main()
