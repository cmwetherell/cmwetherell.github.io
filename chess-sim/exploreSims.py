import pandas as pd
import numpy as np
import sys
import pickle

def main():

    current = pd.read_csv('./chess-sim/data/berlinPoolGames.csv')

    hash_pool = set(pd.util.hash_pandas_object(current[current.played==1])) # gets a hash for each row of the df where the pool game was played
    # hash_ko = ? This hashing technique might not work because the ko games will be different for every grand prix (until the pools are final... maybe thats the only time we care about ko results anyways)
    standings = pickle.load(open( "./chess-sim/data/sims/standings.p", "rb" ) )
    # koGames = pickle.load(open( "./chess-sim/data/sims/koGames.p", "rb" ) )
    poolGames = pickle.load(open( "./chess-sim/data/sims/poolGames.p", "rb" ) )
    simHashesPool = pickle.load(open( "./chess-sim/data/sims/simHashesPool.p", "rb" ) )   
    # simHashesKO = pickle.load(open( "./chess-sim/data/sims/simHashesKO.p", "rb" ) )   

    simMatchPool = [ind for ind, simHash in enumerate(simHashesPool) if hash_pool <= simHash] # checks if all the played games match that simulations games
    # simMatchKO = [ind for ind, simHash in enumerate(simHashesKO) if hash_ko <= simHash] # checks if all the played games match that simulations games

    standings = [standings[i] for i in simMatchPool]
    poolGames = [poolGames[i] for i in simMatchPool]
    # koGames = [koGames[i] for i in simMatchPool]
    
    standings = pd.concat(standings)

    standings['Wins'] = 1 * (standings.event3Points==13) # TODO should move this to simulation function

    # sorry for not naming the dataframes below well... will clean it up later

    df = standings[['Name', 'Qualify', 'gpScore']]
    df_grouped = df.groupby(["Name", "Qualify", "gpScore"]).size().to_frame('Frequency').reset_index()
    
    df_grouped.to_csv('./chess-sim/data/gpOdds.csv', index = False)
    print(df_grouped)

    df3 = standings[['Name', 'Wins', 'event3Points']]
    df3_grouped = df3.groupby(["Name", "Wins", "event3Points"]).size().to_frame('Frequency').reset_index()
    
    df3_grouped.to_csv('./chess-sim/data/gp3Odds.csv', index = False)

    df4 = standings[['Name', 'poolRank', 'pool']]
    df4_grouped = df4.groupby(["Name", 'pool', "poolRank"]).size().to_frame('Frequency').reset_index()
    
    df4_grouped.to_csv('./chess-sim/data/gp3PoolOdds.csv', index = False)

    
if __name__=="__main__":
    main()