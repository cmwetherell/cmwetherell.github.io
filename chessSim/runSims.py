import pandas as pd
from utils import simCandidatesTournament
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

##python poolOdds.py 100 True <- terminal command to get results for 100 sims with new pool draws for GP2

    nSims = 100
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    start_time = time.time()

    with Pool() as p:
        ct =  p.map(simCandidatesTournament, range(nSims))  
        
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()

    pickle.dump(ct, open( "./chessSim/data/sims/ct.p", "wb" ) )
    
    print("--- %s seconds ---" % (time.time() - start_time))

    ct = Counter(ct)
    for key in ct:
        ct[key] /= (nSims / 100)
    print(ct)

if __name__=="__main__":
    main()