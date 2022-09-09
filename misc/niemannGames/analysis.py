import pandas as pd
import numpy as np
from multiprocessing import Pool
from multiprocessing import set_start_method
import lightgbm as lgb
import sys
import pickle
from itertools import repeat

bst = lgb.Booster(model_file = './chessSim/models/model.txt')

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-10, 11, 5)
    
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=model.best_iteration).mean(axis = 0).tolist()
    result = np.random.choice([0,0.5,1], p=preds) 
    # print(whiteElo, blackElo, preds)

    return result

def simGames(gamesData):
    gamesDataLocal = gamesData.copy()
    gamesDataLocal.simResult = 0

    for idx, game in gamesDataLocal.iterrows():
        
        #change Hans Elo to his current live rating
        if game.HansWhite == 0:
            game.blackElo = 2600
        else:
            game.whiteElo = 2600
        
        simulatedResult = chessMLPred(bst, game.whiteElo, game.blackElo)

        if game.HansWhite == 0:
            #can make this one liner with the previous line when not lazy
            simulatedResult = 1 - simulatedResult

        gamesDataLocal.loc[idx, 'simResult'] = simulatedResult

        #simulatedResult is the number of points Hans scored

    return sum(gamesDataLocal['simResult'])

def main():

    terminalArgs = sys.argv

    nSims = 10000
    if len(terminalArgs) > 1:
        nSims = int(terminalArgs[1])

    games = pd.read_csv("./misc/niemannGames/NiemannGames.csv")
    
    #This dataset was taken from 2700Chess, and then I removed games I determined were not classical games (i.e. remove internet games and games that didn't match his classical Elo from FIDE)


    
    with Pool() as p:
        results =  p.map(simGames, repeat(games,nSims))
    # print(results)

    pickle.dump(results, open( "./misc/niemannGames/simulatedResults.p", "wb" ) ) #Save simulations
    
    # print(sum(games['simResult']))
    # print(sum(games['HansResult']))



if __name__=="__main__":
    set_start_method("spawn")
    main()

