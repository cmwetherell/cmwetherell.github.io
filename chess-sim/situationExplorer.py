## want to make this script better TODO

import pandas as pd
from utils import toMD
import pickle

###Not currently using this script, but will utilize when I get around to "what if" posts
def main():

    current = pd.read_csv('./chess-sim/data/berlinPoolGames.csv')
    standings = pickle.load(open( "./chess-sim/data/sims/standings.p", "rb" ) )
    hash = pickle.load(open( "./chess-sim/data/sims/simHashesPool.p", "rb" ) ) 
    print('files read')
    
    unplayed = [idx for idx, val in enumerate(current.played==0) if val == True]
    
    games = []
    for idx in unplayed:
        for whiteScore in [1, 0.5, 0]:
            currentAdj = current.copy()
            
            whiteName = currentAdj.loc[idx, 'whiteName']
            blackName = currentAdj.loc[idx, 'blackName']

            currentAdj.loc[idx, 'played'] = 1
            currentAdj.loc[idx, 'whiteResult'] = whiteScore
            currentAdj.loc[idx, 'blackResult'] = 1 - whiteScore
                         
            nSims, markdown = toMD(currentAdj, standings, hash)           
            games.append([whiteName, blackName, whiteScore, 1 - whiteScore, nSims, markdown])
            print(idx, whiteScore)

    divs = ''

    tables = iter([x[5] for x in games])
    groupTables = [(i, next(tables), next(tables)) for i in tables]

    names = iter([(x[0], x[1]) for x in games[0::3]])  #This selects every 3rd game so we can extract the names without duplicates

    for i, (t1, t2, t3), names in zip(range(8), groupTables, names):
        i+=1
        nm = names[0] + ' vs. ' + names[1]
        # candQual = 'Possibilities for Qualification into Candidates Tournament'
        t1 = t1.replace(" Win ", " Win % ")
        t2 = t2.replace(" Win ", " Win % ")
        t3 = t3.replace(" Win ", " Win % ")

        divs+='**White Wins:** '+nm+'\n{: .'+'w'+str(i)+'}'+'\n\n'+t1+'\n'+'{: .'+'w'+str(i)+'}'+'\n\n'
        divs+='**Draw:** '+nm+'\n{: .'+'d'+str(i)+'}'+'\n\n'+t2+'\n'+'{: .'+'d'+str(i)+'}'+'\n\n'
        divs+='**Black Wins:** '+nm+'\n{: .'+'b'+str(i)+'}'+'\n\n'+t3+'\n'+'{: .'+'b'+str(i)+'}'+'\n\n'
        # print(i)

    with open('./chess-sim/data/whatIfMarkdown.txt', 'wt') as mdTables:
        mdTables.write(divs)
    # pickle.dump(games, open( "gameExplore.p", "wb" ) )
    
    
if __name__=="__main__":
    main()
