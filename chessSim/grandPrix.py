import numpy as np
import pandas as pd
import lightgbm as lgb
import pickle

bst = lgb.Booster(model_file = './chess-sim/models/model.txt')
# preds = pickle.load(open( "./chess-sim/models/preds.p", "rb" ) )

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-20, 6, 20)
    
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=model.best_iteration).mean(axis = 0).tolist()
    result = np.random.choice([0,0.5,1], p=preds) 

    return result



class GrandPrix:
    
    def __init__(self, players, event, overridePool = False, gameData = None):
        '''

        players is a df with name, elo, pool if assigned (include rapid and blitz Elos)

        '''
        # if preds == None:
        #     raise Exception('No preds dict loaded')
        # else:
        #     self.preds = preds

        self.players = players
        self.players['koScore'] = 0
        self.players['koWins'] = 0
        
        self.overridePool = overridePool
        
        self.event = event #e.g. 'event2'
        self.schedule = [] #list of games to play - should it be a dict, probably not. ended up not using this.
        
        self.eventPlayers = self.players.loc[self.players[self.event]==1]
        
        self.gameData = gameData
        self.loadGameData = False
        if self.gameData is None:
            self.gameData = pd.DataFrame() #if gameData is None, create empty DF we can concatenate with
        else:
            self.loadGameData = True #If gameData is not None, we want to load the data and skip the step later
        
        self.koGames = []

    
    def makePools(self, overridePool = False):
        # print(self.eventPlayers)
        
        if (self.event == 'event2') & (not overridePool):
            
            self.poolA = self.eventPlayers[self.eventPlayers['event2Pool']=='A'].copy()
            self.poolB = self.eventPlayers[self.eventPlayers['event2Pool']=='B'].copy()
            self.poolC = self.eventPlayers[self.eventPlayers['event2Pool']=='C'].copy()
            self.poolD = self.eventPlayers[self.eventPlayers['event2Pool']=='D'].copy()
            
            self.poolA['pool'] = 'A'
            self.poolB['pool'] = 'B'
            self.poolC['pool'] = 'C'
            self.poolD['pool'] = 'D'
            
        elif (self.event == 'event3') & (not overridePool):
            
            self.poolA = self.eventPlayers[self.eventPlayers['event3Pool']=='A'].copy()
            self.poolB = self.eventPlayers[self.eventPlayers['event3Pool']=='B'].copy()
            self.poolC = self.eventPlayers[self.eventPlayers['event3Pool']=='C'].copy()
            self.poolD = self.eventPlayers[self.eventPlayers['event3Pool']=='D'].copy()
            
            self.poolA['pool'] = 'A'
            self.poolB['pool'] = 'B'
            self.poolC['pool'] = 'C'
            self.poolD['pool'] = 'D'
        
        else:
            
            poolSort = self.eventPlayers.sort_values(by = 'EloC', axis=0, ascending=False, inplace=False, ignore_index = True)
    
            poolAllocation = []
            alloc = [0,1,2,3]

            for i in range(4):
                np.random.shuffle(alloc)
                poolAllocation.extend(alloc)
            
            self.poolA = poolSort.iloc[[idx for idx, element in enumerate(poolAllocation) if element == 0]].reset_index(drop = True)
            self.poolB = poolSort.iloc[[idx for idx, element in enumerate(poolAllocation) if element == 1]].reset_index(drop = True)
            self.poolC = poolSort.iloc[[idx for idx, element in enumerate(poolAllocation) if element == 2]].reset_index(drop = True)
            self.poolD = poolSort.iloc[[idx for idx, element in enumerate(poolAllocation) if element == 3]].reset_index(drop = True)
            
            self.poolA['pool'] = 'A'
            self.poolB['pool'] = 'B'
            self.poolC['pool'] = 'C'
            self.poolD['pool'] = 'D'
            
    
    def simRoundRobin(self, loadGames, poolGames = None):
        
        if not loadGames:
        
            for pool in self.poolA,self.poolB,self.poolC,self.poolD:

                pairings = [(0,1), (0,2), (0,3), (1,2), (1, 3), (2, 3),
                           (1,0), (2,0), (3,0), (2,1), (3,1), (3,2)]

                poolGames = pd.DataFrame([[
                    pool.iloc[i]['Name'],
                    pool.iloc[j]['Name'],
                    pool.iloc[i]['EloC'],
                    pool.iloc[j]['EloC'],
                    0,
                    0,
                    0
                ] for i,j in pairings],
                    columns = ['whiteName', 'blackName', 'whiteElo', 'blackElo', 'played', 'whiteResult', 'blackResult']
                )

                self.gameData = pd.concat([self.gameData, poolGames]).reset_index(drop = True)
            
        for i, row in self.gameData.iterrows():
            
            if row.played == 0:

                x = chessMLPred(bst, row.whiteElo, row.blackElo)
                # x = np.random.choice([0,0.5,1], p=preds[(row.whiteElo, row.blackElo)])

                self.gameData.loc[i, 'played'] = 1
                self.gameData.loc[i, 'whiteResult'] = x
                self.gameData.loc[i, 'blackResult'] = 1-x


    def simPools(self):
        
        self.poolSummary = pd.DataFrame(np.concatenate(
            (self.gameData[['whiteName', 'whiteResult']].values, self.gameData[['blackName', 'blackResult']].values)
            , axis = 0))
        self.poolSummary.columns = ['name', 'result']
        self.poolSummary['wins'] = 1 * (self.poolSummary.result == 1)
        self.poolSummary = self.poolSummary.groupby(['name']).agg(
             score = ('result','sum'),
             wins = ('wins','sum'),
             ).reset_index()
        
        self.poolA = self.poolA.merge(self.poolSummary, how = 'left', left_on = "Name", right_on = "name")
        self.poolB = self.poolB.merge(self.poolSummary, how = 'left', left_on = "Name", right_on = "name")
        self.poolC = self.poolC.merge(self.poolSummary, how = 'left', left_on = "Name", right_on = "name")
        self.poolD = self.poolD.merge(self.poolSummary, how = 'left', left_on = "Name", right_on = "name")
        
        for pool in self.poolA,self.poolB,self.poolC,self.poolD:
            
            pool['poolScore'] = 0
            pool['poolWins'] = 0
            pool['poolRank'] = 0
            pool[self.event+'Points'] = 0
 
            pool.poolScore = pool.score
            pool.poolWins = pool.wins
            
            pool.drop(labels=['score', 'wins'], inplace=True, axis = 1)
            
            z = pool['poolScore'].value_counts().sort_index(ascending = False)
            rankedPlayers = 1
            for j, i in z.iteritems():
                pool.loc[pool['poolScore'] == j, 'poolRank'] = rankedPlayers
                rankedPlayers += i
            
            
            tbPool = pool[pool['poolScore'] == max(pool['poolScore'])].reset_index(drop = True).copy()
            
            if tbPool.shape[0] == 2:
                
                winner = 1 - self.headsUpMatch(startingControl = 'r' ##winner = 0 if first wins, 1 if second wins
                             ,ELC = tbPool.iloc[1]['EloC']
                             ,EHC = tbPool.iloc[0]['EloC']
                             ,ELR = tbPool.iloc[1]['EloR']
                             ,EHR = tbPool.iloc[0]['EloR']
                             ,ELB = tbPool.iloc[1]['EloB']
                             ,EHB = tbPool.iloc[0]['EloB'])                

                pool.loc[pool.Name == tbPool.iloc[winner]['Name'], 'poolRank'] = 1
                pool.loc[pool.Name == tbPool.iloc[(1-winner)]['Name'], 'poolRank'] = 2
            
            elif tbPool.shape[0] == 3:
                tbPool['tbPointsR'] = 0
                
                whiteRand = np.random.randint(2)
                
                pairings = [(0,1, whiteRand),(0,2, (1-whiteRand)),(1,2, whiteRand)]

                for favorite, underdog, white in pairings:
                    
                    if white == 0:
                        x = chessMLPred(bst, pool.iloc[underdog]['EloC'], pool.iloc[favorite]['EloC'])
                    else:
                        x = 1 - chessMLPred(bst, pool.iloc[favorite]['EloC'], pool.iloc[underdog]['EloC'])

                    tbPool.loc[underdog, 'tbPointsR'] += x                
                    tbPool.loc[favorite, 'tbPointsR'] += (1-x)
                
                tbPool2 = tbPool[tbPool['tbPointsR'] == max(tbPool['tbPointsR'])].reset_index(drop = True).copy()
                    
                if tbPool2.shape[0] == 1:
                    pool.loc[pool.Name == tbPool2['Name'].item(), 'poolRank'] = 1
                    pool.loc[(pool.poolRank!= 4) & (pool.Name != tbPool2['Name'].item()), 'poolRank'] = 2
               
                if tbPool2.shape[0] == 2:
                    winner = 1 - self.headsUpMatch(startingControl = 'b' ##winner = 0 if first player wins, 1 if second wins
                             ,ELC = tbPool2.iloc[1]['EloC']
                             ,EHC = tbPool2.iloc[0]['EloC']
                             ,ELR = tbPool2.iloc[1]['EloR']
                             ,EHR = tbPool2.iloc[0]['EloR']
                             ,ELB = tbPool2.iloc[1]['EloB']
                             ,EHB = tbPool2.iloc[0]['EloB'])
                    
                    thirdPlaceName = tbPool.Name[tbPool.tbPointsR == min(tbPool.tbPointsR)].item()

                    pool.loc[pool.Name == tbPool2.iloc[winner]['Name'], 'poolRank'] = 1
                    pool.loc[pool.Name == tbPool2.iloc[(1-winner)]['Name'], 'poolRank'] = 2
                    pool.loc[pool.Name == thirdPlaceName, 'poolRank'] = 3 #TODO:
 
                    # pool.loc[pool.poolRank not in [1,2,3], 'poolRank'] = 4
                
                if tbPool2.shape[0] == 3:
                    tbPool2['tb2PointsR'] = 0
                
                    whiteRand = np.random.randint(2)

                    pairings = [(0,1, whiteRand),(0,2, (1-whiteRand)),(1,2, whiteRand)]


                    for favorite, underdog, white in pairings:

                        if white == 0:
                            x = chessMLPred(bst, pool.iloc[underdog]['EloC'], pool.iloc[favorite]['EloC'])
                        else:
                            x = 1 - chessMLPred(bst, pool.iloc[favorite]['EloC'], pool.iloc[underdog]['EloC'])

                        tbPool2.loc[underdog, 'tb2PointsR'] += x                
                        tbPool2.loc[favorite, 'tb2PointsR'] += (1-x)

                    tbPool3 = tbPool2[tbPool2['tb2PointsR'] == max(tbPool2['tb2PointsR'])].reset_index(drop = True).copy()
                    
                    if tbPool2.shape[0] == 1:
                        pool.loc[pool.Name == tbPool3['Name'].item(), 'poolRank'] = 1
                        pool.loc[(pool.poolRank!= 4) & (pool.Name != tbPool3['Name'].item()), 'poolRank'] = 2
                        # pool.loc[pool.poolRank not in [1,2,3], 'poolRank'] = 4 #TODO
                        
                    if tbPool2.shape[0] > 1: #if noone won the blitz RR, just randomize.
                        randWinner = np.random.randint(0,3)
                        pool.loc[pool.Name == tbPool2.loc[randWinner, 'Name'], 'poolRank'] = 1
                        pool.loc[(pool.poolRank!= 4) & (pool.Name != tbPool2.loc[randWinner, 'Name']), 'poolRank'] = 2

                        # pool.loc[pool.poolRank not in [1,2,3], 'poolRank'] = 4
             
            elif tbPool.shape[0] == 4:
                
                winner = self.headsUpMatch(startingControl = 'r' ##winner = 0 if favorite wins, 1 if second wins
                             ,ELC = tbPool.iloc[3]['EloC']
                             ,EHC = tbPool.iloc[0]['EloC']
                             ,ELR = tbPool.iloc[3]['EloR']
                             ,EHR = tbPool.iloc[0]['EloR']
                             ,ELB = tbPool.iloc[3]['EloB']
                             ,EHB = tbPool.iloc[0]['EloB'])
                
                if winner == 0:
                    pool.loc[pool.Name == tbPool.iloc[3]['Name'], 'poolRank'] = 3
                else:                    
                    pool.loc[pool.Name == tbPool.iloc[0]['Name'], 'poolRank'] = 3
                
                winner = self.headsUpMatch(startingControl = 'r' ##winner = 0 if first player wins, 1 if second wins
                             ,ELC = tbPool.iloc[2]['EloC']
                             ,EHC = tbPool.iloc[1]['EloC']
                             ,ELR = tbPool.iloc[2]['EloR']
                             ,EHR = tbPool.iloc[1]['EloR']
                             ,ELB = tbPool.iloc[2]['EloB']
                             ,EHB = tbPool.iloc[1]['EloB'])
                
                if winner == 0:
                    pool.loc[pool.Name == tbPool.iloc[2]['Name'], 'poolRank'] = 3
                else:                    
                    pool.loc[pool.Name == tbPool.iloc[1]['Name'], 'poolRank'] = 3

                tbFinal = pool[pool['poolRank'] != 3].reset_index(drop = True).copy()

                
                winner = self.headsUpMatch(startingControl = 'r' ##winner = 0 if first player wins, 1 if second wins
                             ,ELC = tbFinal.iloc[1]['EloC']
                             ,EHC = tbFinal.iloc[0]['EloC']
                             ,ELR = tbFinal.iloc[1]['EloR']
                             ,EHR = tbFinal.iloc[0]['EloR']
                             ,ELB = tbFinal.iloc[1]['EloB']
                             ,EHB = tbFinal.iloc[0]['EloB'])
                
                if winner == 0:
                    pool.loc[pool.Name == tbFinal.iloc[0]['Name'], 'poolRank'] = 2
                    pool.loc[pool.Name == tbFinal.iloc[1]['Name'], 'poolRank'] = 1
                else:                    
                    pool.loc[pool.Name == tbFinal.iloc[0]['Name'], 'poolRank'] = 1
                    pool.loc[pool.Name == tbFinal.iloc[1]['Name'], 'poolRank'] = 2

        self.players = pd.concat([self.poolA, self.poolB, self.poolC, self.poolD], ignore_index=True)


    def headsUpMatch(self, startingControl, ELC, EHC, ELR, EHR, ELB, EHB , uName = None, fName = None, ko = None):
        #TODO: faster time controls should draw less often
        #startingControl: 'c' = classical, else go to rapid start
        ##Thsi code needs to be refactored... ideally have a tournament, match, and player class that can be used.
        
        
        x = chessMLPred(bst, ELC, EHC) #this function returns the score for white; x = score for white
        y = 1 - chessMLPred(bst, EHC, ELC) #y = score for black
        
        self.koGames.append([uName, fName, x, 'cko'])
        self.koGames.append([fName, uName, 1-y, 'cko'])

        #TODO: Add koGames for tiebreaks that are not heads up matches; specify where HU match came from (pool tie breaks, or KO)

        '''
        saving this code so that I can reuse it during the KO portion of Berlin Leg 3


        if((self.event == 'event2') & (uName =='Anish Giri') & (ko == 'semi')):
            x = 0.5 # 1 if white wins # Giri wins if 1
            y = 0.5 # 1 if black wins #Giri wins if 1
            pass
        if((self.event == 'event2') & (uName =='Maxime Vachier-Lagrave') & (ko == 'semi')):
            x = 0.5 # 1 if white wins #MVL wins if 1  for x or y
            y = 0.0 # 1 if black wins
            pass
        
        if((self.event == 'event2') & (ko != 'semi')):
            # x = 0.5 # 1 if white wins #MVL wins if 1  for x or y
            y = 0.5 # 1 if black wins
            pass
        
        self.koGames.append([uName, fName, x, 'cko'])
        self.koGames.append([fName, uName, 1-y, 'cko'])
        '''
        

        
        if (startingControl == 'c') & (uName != None) & (fName != None):

            self.players.loc[self.players.Name == uName,'koScore'] += x
            self.players.loc[self.players.Name == fName, 'koScore'] += (1-x)

            self.players.loc[self.players.Name == uName,'koWins'] += 1 * (x == 1)
            self.players.loc[self.players.Name == fName, 'koWins'] += 1 * ((1-x) == 1)
            
            self.players.loc[self.players.Name == uName,'koScore'] += y
            self.players.loc[self.players.Name == fName, 'koScore'] += (1-y)

            self.players.loc[self.players.Name == uName,'koWins'] += 1 * (y == 1)
            self.players.loc[self.players.Name == fName, 'koWins'] += 1 * ((1-y) == 1)

        
        
        if (startingControl == 'c') & ((x + y) > (1-x) + (1-y)):
            return 0
        elif (startingControl == 'c') & ((x + y) < (1-x) + (1-y)):
            return 1
        
        elif (startingControl != 'c') | ((x + y) == (1-x) + (1-y)):
            
            x = chessMLPred(bst, ELR, EHR)
            y = 1 - chessMLPred(bst, EHR, ELR)
            
            # if((self.event == 'event2') & (uName =='Anish Giri') & (ko == 'semi')):
            #     x = 0 # 1 if white wins 
            #     y = 0.5 # 1 if black wins 
            #     pass
            
            self.koGames.append([uName, fName, x, 'rko'])
            self.koGames.append([fName, uName, 1-y, 'rko'])
            
            if  ((x + y) > (1-x) + (1-y)):
                return 0
            elif ((x + y) < (1-x) + (1-y)):
                return 1
        
            elif (startingControl != 'r') | ((x + y) == (1-x) + (1-y)):
            
                x = chessMLPred(bst, ELB, EHB)
                y = 1 - chessMLPred(bst, EHB, ELB)
                        
                self.koGames.append([uName, fName, x, 'bko'])
                self.koGames.append([fName, uName, 1-y, 'bko'])

                if (x + y) > ((1-x) + (1-y)):
                    return 0
                elif  (x + y) < ((1-x) + (1-y)):
                    return 1

                elif (x + y) == ((1-x) + (1-y)):
                    self.koGames.append([uName, fName, -999, 'armageddonko'])
                    return np.random.randint(2) #If tied after Blitz, just randomize, don't sim Armageddon


                else:
                    raise Exception('Bad math!')
                
            else:
                raise Exception('Bad math!')
                
        else:
            raise Exception('Bad math!')
        
    
    def simKnockout(self):
        self.players['knockouts'] = 0
        # print(self.players)
        
        knockoutPool = self.players[self.players.poolRank == 1]
        name0 = knockoutPool.iloc[0]['Name']
        name1 = knockoutPool.iloc[1]['Name']
        name2 = knockoutPool.iloc[2]['Name']
        name3 = knockoutPool.iloc[3]['Name']
        
        
        
        winner = self.headsUpMatch(startingControl = 'c' ##winner = 0 if first player wins, 1 if second wins
             ,ELC = knockoutPool.iloc[1]['EloC']
             ,EHC = knockoutPool.iloc[0]['EloC']
             ,ELR = knockoutPool.iloc[1]['EloR']
             ,EHR = knockoutPool.iloc[0]['EloR']
             ,ELB = knockoutPool.iloc[1]['EloB']
             ,EHB = knockoutPool.iloc[0]['EloB']
                                  ,uName = name1
                                  ,fName = name0, ko = 'semi')

        if winner == 0:
            self.players.loc[self.players.Name == knockoutPool.iloc[1]['Name'], 'knockouts'] = 1
        if winner == 1:
            self.players.loc[self.players.Name == knockoutPool.iloc[0]['Name'], 'knockouts'] = 1
            
            
        winner = self.headsUpMatch(startingControl = 'c' ##winner = 0 if favorite wins, 1 if second wins
             ,ELC = knockoutPool.iloc[3]['EloC']
             ,EHC = knockoutPool.iloc[2]['EloC']
             ,ELR = knockoutPool.iloc[3]['EloR']
             ,EHR = knockoutPool.iloc[2]['EloR']
             ,ELB = knockoutPool.iloc[3]['EloB']
             ,EHB = knockoutPool.iloc[2]['EloB']
                                  ,uName = name3
                                  ,fName = name2, ko = 'semi')

        if winner == 0:
            self.players.loc[self.players.Name == knockoutPool.iloc[3]['Name'], 'knockouts'] = 1
        if winner == 1:
            self.players.loc[self.players.Name == knockoutPool.iloc[2]['Name'], 'knockouts'] = 1
        
        knockoutPool = self.players[self.players.knockouts == 1]
        
        name0 = knockoutPool.iloc[0]['Name']
        name1 = knockoutPool.iloc[1]['Name']
        
        winner = self.headsUpMatch(startingControl = 'c' ##winner = 0 if first player wins, 1 if second wins
             ,ELC = knockoutPool.iloc[1]['EloC']
             ,EHC = knockoutPool.iloc[0]['EloC']
             ,ELR = knockoutPool.iloc[1]['EloR']
             ,EHR = knockoutPool.iloc[0]['EloR']
             ,ELB = knockoutPool.iloc[1]['EloB']
             ,EHB = knockoutPool.iloc[0]['EloB']
                                  ,uName = name1
                                  ,fName = name0)

        if winner == 0:
            self.players.loc[self.players.Name == knockoutPool.iloc[1]['Name'], 'knockouts'] = 2
        if winner == 1:
            self.players.loc[self.players.Name == knockoutPool.iloc[0]['Name'], 'knockouts'] = 2
    
    def assignPoints(self):
        
        for pool in ['A','B','C','D']:
            poolPointsDF = self.players[self.players.pool == pool]
            z = poolPointsDF['poolRank'].value_counts().sort_index()
            
            for j, i in z.iteritems():
                
                if i == 1:
                    if j == 1:
                        points = 7
                    elif j == 2:
                        points = 4
                    elif j == 3:
                        points = 2
                    elif j ==4 :
                        points = 0
                    else:
                        print(poolPointsDF)
                        raise Exception('Invalid pool rank')
                    
                    self.players.loc[(self.players.pool == pool) & (self.players.poolRank == j), self.event+'Points'] = points
                    
                if i == 2:
                    if j == 1:
                        raise Exception('Cant be tied for first')
                    elif j == 2:
                        points = 3
                    elif j == 3:
                        points = 1
                    elif j ==4 :
                        raise Exception('Two tied for fourth?')
                    else:
                        raise Exception('Invalid pool rank')
                        
                    self.players.loc[(self.players.pool == pool) & (self.players.poolRank == j), self.event+'Points'] = points
                
                if i == 3:
                    if j == 1:
                        raise Exception('Cant be tied for first')
                    elif j == 2:
                        points = 2
                    elif j == 3:
                        raise Exception('Three tied for third?')
                    elif j ==4 :
                        raise Exception('Three ties for fourth?')
                    else:
                        raise Exception('Invalid pool rank')
                        
                    self.players.loc[(self.players.pool == pool) & (self.players.poolRank == j), self.event+'Points'] = points
            
            
        self.players[self.event+'Points'] += self.players.knockouts * 3
        self.players.GP += self.players.poolScore + self.players.koScore
        self.players.GW += self.players.poolWins + self.players.koWins
            
    def simGP(self):
        
        self.makePools(self.overridePool)
        self.simRoundRobin(self.loadGameData, self.gameData)
        self.simPools()
        self.simKnockout()
        self.assignPoints()