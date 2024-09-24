import pandas as pd
import time
import sys
import pickle
from tqdm import tqdm
from collections import Counter
import lightgbm as lgb
from utils import upload_dataframe_to_db
from simOlympiad import main as simOlympiad

def main():
    start_time = time.time()
    terminalArgs = sys.argv

    nSims = 100
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    results = []
    for i in tqdm(range(nSims), desc="Simulating"):
        try:
            result = simOlympiad(i)
            results.append(result)
        except Exception as e:
            print(f"An error occurred during simulation {i}: {e}")

    print(f"--- {time.time() - start_time} seconds ---")

    winsByRound = [results]
    print('dumping')
    pickle.dump(winsByRound, open("./chessSim/data/sims/olympiad45.p", "wb"))
    print('done dumping')

    df = pd.DataFrame(winsByRound[0])
    df.columns = ['gold', 'silver', 'bronze']
    df['round'] = '9'
    df['future_results'] = ""

    table_name = 'olympiad_2024'
    upload_dataframe_to_db(table_name, df)
    print("DataFrame uploaded to the database successfully.")

    ct = Counter([x[0] for x in results])
    for key in ct:
        ct[key] /= (nSims / 100)
    print('winners results', ct)

    print(f"--- {time.time() - start_time} seconds ---")
    print((time.time() - start_time) / nSims)

if __name__ == "__main__":
    main()
