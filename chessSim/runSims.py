from re import I
import pandas as pd
from utils import summarizeCurrent
# from utils import simNorway
# from utils import simSuperbet
from multiprocessing import Pool
from itertools import repeat
import time
import sys
import pickle
from tqdm import tqdm
import time
from collections import Counter
from multiprocessing import set_start_method
import lightgbm as lgb
import json
import gzip
from utils import upload_dataframe_to_db 


from simOlympiad import main as simOlympiad

# from scrape2700 import * #Used to refresh live ratings after a round, so I don't forget to do it manually. Might not do this for 24 candidates.

# from sinquefieldCup import main as SCup
# from utils import simCandidatesTournament as simCand
# from utils import simWomensCandidatesTournament as simCand

def main():
    start_time = time.time()

    terminalArgs = sys.argv
    # current = pd.read_csv("./chessSim/data/candidatesGames2024.csv")
    # # current = pd.read_csv("./chessSim/data/womensCandidatesGames2024.csv")
    # # # print(current)

    # currentResults = summarizeCurrent(current)
    # # pickle.dump(currentResults, open( "./chessSim/data/sims/candidatesSummary.p", "wb" ) ) #Save simulations

    # print(currentResults)
    # gameModel = lgb.Booster(model_file = './chessSim/models/model.txt')

### python poolOdds.py 100 True <- termi
# nal command to get results for 100 sims with new pool draws for GP2

    nSims = 160
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    with Pool() as p:
        try:
            # Use imap_unordered for potentially faster execution since the order of results may not matter
            # Wrap the repeat iterable with tqdm to show progress, specifying the total number of tasks
            results = list(tqdm(p.imap_unordered(simOlympiad, range(nSims)), total=nSims, desc="Simulating"))
            # without tqdm
            # results = list(p.imap_unordered(simOlympiad, range(nSims)))
        except Exception as e:
            print(f"An error occurred during simulation: {e}")
        finally:
            p.close()
            p.join()


    print("--- %s seconds ---" % (time.time() - start_time))
    # print(results)
    # print('\n\n\n\n\n')

    winsByRound = []

    winsByRound.append(results)

    print('dumping')

    pickle.dump(winsByRound, open( "./chessSim/data/sims/olympiad45.p", "wb" ) ) #Save simulations

    print('done dumping')

    # Convert the loaded data back into a DataFrame if necessary
    # Assuming `wins_by_round` is a list of results, convert it to a DataFrame
    df = pd.DataFrame(winsByRound[0])  # Adjust indexing if needed

    # change column names to 'gold', 'silver', 'bronze'
    df.columns = ['gold', 'silver', 'bronze']
    print(df)

    df['round'] = 'Pre'
    df['future_results'] = "" # empty string for future results

    # Define the table name for the upload
    table_name = 'olympiad_2024'  # Replace with your desired table name

    # Upload the DataFrame to the database
    upload_dataframe_to_db(table_name, df)

    print("DataFrame uploaded to the database successfully.")

    # create a Counter with the first element of each element in results, expeess as a % of nSims and print it
    ct = Counter([x[0] for x in results])
    for key in ct:
        ct[key] /= (nSims / 100)
    print('winners results', ct)


    # print(winsByRound)

    # winners, seconds, ties, simulation_results = zip(*results)

    # ct = Counter(winners)
    # for key in ct:
    #     ct[key] /= (nSims / 100)
    # print('winners results', ct)

    # ct = Counter(seconds)
    # for key in ct:
    #     ct[key] /= (nSims / 100)
    # print('seconds results', ct)

    # ct = Counter(ties)
    # for key in ct:
    #     ct[key] /= (nSims / 100)
    # print('tie results', ct)

    ## Create Bar chart of magnusElo with plotly express

    # import plotly.express as px

    # df = pd.DataFrame.from_dict(magnusElo, orient='index').reset_index()
    # df.columns = ['elo', 'percent']
    # df = df.sort_values(by = 'elo')
    # fig = px.bar(df, x="elo", y="percent", title='Magnus Elo')

    # #change color of bars
    # fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
    #             marker_line_width=1.5, opacity=0.6)


    # fig.show()
        # start_time = time.time()

    # print('dumping')

    # pickle.dump(winners, open( "./chessSim/data/sims/candidatesWinners_.p", "wb" ) ) #Save simulations
    # pickle.dump(seconds, open( "./chessSim/data/sims/candidatesSeconds_.p", "wb" ) ) #Save simulations
    # pickle.dump(ties, open( "./chessSim/data/sims/candidatesTies_.p", "wb" ) ) #Save simulations

    # # # Compress and save to a gzip file
    # with gzip.open('./chessSim/data/sims/candidates_womens_results.json.gz', 'wt', encoding='UTF-8') as file:
    #     json.dump(simulation_results, file)


    # # print('done dumping')
    # # print(winsByRound)

        
    print("--- %s seconds ---" % (time.time() - start_time))
    # print time per nSim in seconds
    print((time.time() - start_time)/nSims)

    
if __name__=="__main__":
    set_start_method("spawn")
    main()

