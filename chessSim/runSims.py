import pandas as pd
from utils import simCandidatesTournament
from utils import simNorway
from utils import simSuperbet
from multiprocessing import Pool
from itertools import repeat
import time
import sys
import pickle
from tqdm import tqdm
import time
from collections import Counter



##Run this script with Override True and False to see the impact of the pool drawing on results. GP2 w and wo pools, Overall Qualification impact. 
def main():

    terminalArgs = sys.argv
    current = pd.read_csv("./chessSim/data/superbetGames.csv")

##python poolOdds.py 100 True <- terminal command to get results for 100 sims with new pool draws for GP2

    nSims = 100
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    
    inputs = zip(
        repeat(current, nSims),
    )

    start_time = time.time()
 
    with Pool() as p:
        results =  p.starmap(simSuperbet, tqdm(inputs, total = nSims))
        
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()

    pickle.dump(results, open( "./chessSim/data/sims/superbet.p", "wb" ) ) #Save simulations
    
    print("--- %s seconds ---" % (time.time() - start_time))

    winners = [winner for winner, _, _ in results]
    magnusElo = [Elo for _, Elo, _ in results]
    allElo = [EloDict for _, _, EloDict in results]

    # pickle.dump(magnusElo, open( "./chessSim/data/sims/magnusEloSims.p", "wb" ) ) #Save simulations
    # pickle.dump(allElo, open( "./chessSim/data/sims/allElo.p", "wb" ) ) #Save simulations

    # ct = Counter(magnusElo)
    # for key in ct:
    #     ct[key] /= (nSims / 100)
    # print(ct)

    ct = Counter(winners)
    for key in ct:
        ct[key] /= (nSims / 100)
    print(ct)

if __name__=="__main__":
    main()