from re import I
import pandas as pd
from utils import simCandidatesTournament
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

# from sinquefieldCup import main as SCup
from utils import simTata

def main():

    terminalArgs = sys.argv
    current = pd.read_csv("./chessSim/data/tataSteelGames.csv")

# ##python poolOdds.py 100 True <- terminal command to get results for 100 sims with new pool draws for GP2

    nSims = 10000
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])
    
    # winsByRound = []

    # print(i, time.time())
    
    start_time = time.time()

    with Pool() as p:
        results =  p.map(simTata, repeat(current,nSims))

    print("--- %s seconds ---" % (time.time() - start_time))
    # print(results)

    winners = [winner for winner, _ in results]
    ties = [ties for _, ties in results]

    ct = Counter(winners)
    for key in ct:
        ct[key] /= (nSims / 100)
    print('results', ct)

    ct = Counter(ties)
    for key in ct:
        ct[key] /= (nSims / 100)
    print('results', ct)
        # start_time = time.time()

    print('dumping')

    pickle.dump(winners, open( "./chessSim/data/sims/tataSteelSims.p", "wb" ) ) #Save simulations

    print('done dumping')
    # print(winsByRound)


        
        # print("--- %s seconds ---" % (time.time() - start_time))

    
if __name__=="__main__":
    set_start_method("spawn")
    main()

