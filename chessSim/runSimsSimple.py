import pandas as pd
import time
import sys
import pickle
from tqdm import tqdm
from collections import Counter
import lightgbm as lgb
from utils import upload_dataframe_to_db
from utils import simWCC

def main():
    start_time = time.time()
    terminalArgs = sys.argv

    nSims = 10000
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    results = []
    for i in tqdm(range(nSims), desc="Simulating"):
        try:
            result = simWCC(None)
            results.append(result)
        except Exception as e:
            print(f"An error occurred during simulation {i}: {e}")

    print(f"--- {time.time() - start_time} seconds ---")

    # Process results into a DataFrame
    all_rows = []
    for result in results:
        base_row = {
            'winner': result['winner'],
            'tie': result['tie']
        }
        game_outcomes = {f"{game['gameId']}|{str(int(game['round']))}": game['outcome'] for game in result['games']}
        all_rows.append({**base_row, **game_outcomes})

    # Create DataFrame
    df = pd.DataFrame(all_rows)

    # winsByRound = [results]
    # print('dumping')
    # pickle.dump(winsByRound, open("./chessSim/data/sims/olympiad45.p", "wb"))
    # print('done dumping')

    # df = pd.DataFrame(winsByRound[0])
    # df.columns = ['gold', 'silver', 'bronze']
    # df['round'] = '9'
    # df['future_results'] = ""

    df['round'] = 0

    table_name = 'wcc24'
    upload_dataframe_to_db(table_name, df, if_exists='replace')
    print("DataFrame uploaded to the database successfully.")

    ct = Counter([x['winner'] for x in results])
    for key in ct:
        ct[key] /= (nSims / 100)
    print('winners results', ct)

    print(f"--- {time.time() - start_time} seconds ---")
    print((time.time() - start_time) / nSims)

if __name__ == "__main__":
    main()
