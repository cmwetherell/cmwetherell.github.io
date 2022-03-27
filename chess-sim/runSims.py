import pandas as pd
from utils import simGrandPrix
from multiprocessing import Pool
from itertools import repeat
import time
import sys
import pickle
from tqdm import tqdm
import time



##Run this script with Override True and False to see the impact of the pool drawing on results. GP2 w and wo pools, Overall Qualification impact. 
def main():

    terminalArgs = sys.argv

##python poolOdds.py 100 True <- terminal command to get results for 100 sims with new pool draws for GP2

    nSims = 100
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])
        
    resetPools = False #Option to test the impact of redrawing the pools
    if len(terminalArgs) > 2:
        resetPools = terminalArgs[2]

    gpData = pd.read_csv('./chess-sim/data/gpEloData.csv')
    current = pd.read_csv('./chess-sim/data/berlinPoolGames.csv')
    # preds = pickle.load(open( "./chess-sim/models/preds.p", "rb" ) )
    
    print('running sims: ', nSims)
    inputs = zip(
        repeat(gpData, nSims),
        repeat(resetPools, nSims),
        repeat(current, nSims)
        # repeat(preds, nSims)
    )

    start_time = time.time()

    with Pool() as p:
        gp =  p.starmap(simGrandPrix, tqdm(inputs, total = nSims)
                            ) #set override pools = True to change pools    
        
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()


    # list comprehension
    standings = [fs for fs, _, _ in gp]
    poolGames = [poolGames for _, poolGames, _ in gp]
    koGames = [koGames for _, _, koGames in gp]
    
    # The hashes are necessary for running 'what-if' scenarios in the pool stages
    # This approach means we don't have to save all the data from each simulation.
    simHashesPool = [(set(pd.util.hash_pandas_object(df))) for df in poolGames]
    simHashesKO = [(set(pd.util.hash_pandas_object(df))) for df in koGames]
    
    # poolGames[0].to_csv('./chess-sim/data/berlinPoolGames.csv', index = False) #to get a copy of the dataframe needed for scenario analysis with hashes.


    pickle.dump(standings, open( "./chess-sim/data/sims/standings.p", "wb" ) )
    pickle.dump(poolGames, open( "./chess-sim/data/sims/poolGames.p", "wb" ) )
    pickle.dump(koGames, open( "./chess-sim/data/sims/koGames.p", "wb" ) )
    pickle.dump(simHashesPool, open( "./chess-sim/data/sims/simHashesPool.p", "wb" ) )
    pickle.dump(simHashesKO, open( "./chess-sim/data/sims/simHashesKO.p", "wb" ) )
    
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__=="__main__":
    main()