from math import remainder
import pandas as pd
import pickle
from player import Player
import numpy as np
import itertools
import lightgbm as lgb
import random

def getNorway(): 
    candidates = pickle.load(open( "./chessSim/data/playerData.p", "rb" ) )
    candidates = candidates[candidates.Name.isin(['Carlsen','Rapport', 'So', 'Mamedyarov', 'Giri', 'Radjabov', 'Anand', 'Vachier-Lagrave', 'Topalov', 'Wang Hao' ])]
    candidates = {x[0]: Player(x[0], x[1], x[2] , x[3]) for x in np.array(candidates)}
    return candidates

bst = lgb.Booster(model_file = './chessSim/models/model.txt')

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-10, 11, 5)
    
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=model.best_iteration).mean(axis = 0).tolist()
    result = np.random.choice([0,0.5,1], p=preds)

    return result

def playChess(model, whitePlayer, blackPlayer, format):

    whiteElo = getattr(whitePlayer, 'Elo' + format.upper()) #Get the Elo[C] attribute value from Player class
    blackElo = getattr(blackPlayer, 'Elo' + format.upper())

    result = chessMLPred(model, whiteElo, blackElo) #points white player scored
    # if whitePlayer.name == 'Carlsen':
    #     result = 1
    # if blackPlayer.name == 'Carlsen':
    #     result = 0
    whitePlayer.addGame(result, whiteElo, blackElo, format)
    blackPlayer.addGame((1 - result), blackElo, whiteElo, format)

    return result

class Norway:
    
    def __init__(self, players, games = None):
        self.players = players
        self.playerNames = players.keys()
        self.games = games
        self.loadGames = self.games != None

    def createGames(self):
        s1Games = list(itertools.combinations(self.playerNames, 2))
        random.shuffle(s1Games)
        white = {name: 0 for name in self.playerNames} #to track how many white games each player has
        rrGames = []
        for i, j in s1Games:
            if white[i] > white[j]:
                white[j] += 1
                rrGames.append((j, i))
            elif white[i] < white[j]:
                white[i] += 1
                rrGames.append((i, j))
            elif white[i] == white[j]:
                k = random.randint(0, 1)
                if k == 0:
                    white[i] += 1
                    rrGames.append((i, j))
                if k == 1:
                    white[j] += 1
                    rrGames.append((j, i))
        
        games = pd.DataFrame([[game[0], game[1]] for game in rrGames], columns = ['whitePlayer', 'blackPlayer'])

        self.games = games

    def simRR(self):

        stage = 'rr'

        self.games['format'] = 'c'
        self.games['stage'] = stage
        self.games['played'] = 0
        self.games['result'] = 0

        for idx, row in self.games.iterrows():
            whitePlayer = self.players[row.whitePlayer]
            blackPlayer = self.players[row.blackPlayer]

            self.games.at[idx, 'played'] = 1
            result = playChess(bst, whitePlayer, blackPlayer, format = 'c') #points white player scored
            self.games.at[idx, 'result'] = result
        
        # self.games = pd.concat([self.games, games], ignore_index = True, axis = 0)

        whiteResults = self.games[['whitePlayer', 'result']].values
        blackResults = self.games[['blackPlayer', 'result']].values
        blackResults[:, 1] = 1 - blackResults[:, 1] # to change the game results to black player POV

        self.rrSummary = pd.DataFrame(np.concatenate(
            (whiteResults, blackResults)
            , axis = 0))
        self.rrSummary.columns = ['name', 'result']
        self.rrSummary['wins'] = 1 * (self.rrSummary.result == 1)
        self.rrSummary = self.rrSummary.groupby(['name']).agg(
            score = ('result','sum'),
            wins = ('wins','sum'),
            ).sort_values(by = ['score', 'wins'], ascending = False).reset_index()
        self.rrSummary['first'] = 1 * (self.rrSummary.score == max(self.rrSummary.score))

        self.remaining = list(self.rrSummary[self.rrSummary['first'] == 1].name)
        if len(self.remaining) == 1:
            self.winner = self.remaining[0]
    
    def ties(self):
        if len(self.remaining) == 2:

            player1 = self.players[self.remaining[0]]
            player2 = self.players[self.remaining[1]]

            game1 = playChess(bst, player1, player2, format = 'b') #points white player scored
            self.games.loc[self.games.shape[0]] = [player1.name, player2.name, 'b', 't1', 1, game1]

            game2 = playChess(bst, player2, player1, format = 'b') #points white player scored
            self.games.loc[self.games.shape[0]] = [player2.name, player1.name, 'b', 't1', 1, game2]


            player1Score = game1 + (1 - game2)

            if player1Score > 1:
                self.winner = player1.name
            elif player1Score == 1:
                self.winner = random.choice([player1.name, player2.name]) #armageddon
            elif player1Score < 1:
                self.winner = player2.name
     
        elif len(self.remaining) > 2:
            rrGames = list(itertools.combinations(self.playerNames, 2))
            switchSides = [(x[1], x[0]) for x in rrGames]
            rrGames.extend(switchSides)
            rrGames.sort()
            tbGames = pd.DataFrame([[game[0], game[1]] for game in rrGames], columns = ['whitePlayer', 'blackPlayer'])

            tbGames['played'] = 0
            tbGames['result'] = 0
            tbGames['blackWin'] = 0

            for idx, row in tbGames.iterrows():
                whitePlayer = self.players[row.whitePlayer]
                blackPlayer = self.players[row.blackPlayer]

                tbGames.at[idx, 'played'] = 1
                result = playChess(bst, whitePlayer, blackPlayer, format = 'b') #points white player scored

                #TODO should I use the update ratings function or not?
                tbGames.at[idx, 'result'] = result
        
            whiteResults = tbGames[['whitePlayer', 'blackPlayer', 'result', 'blackWin']].values
            blackResults = tbGames[['blackPlayer', 'whitePlayer', 'result', 'blackWin']].values
            blackResults[:, 2] = 1 - blackResults[:, 2] # to change the game results to black player POV
            blackResults[:, 3] = 1 * (blackResults[:, 2] == 1) #checking for black wins, used for tb
            
            self.tbrrSummary = pd.DataFrame(np.concatenate(
                (whiteResults, blackResults)
                , axis = 0))
            self.tbrrSummary.columns = ['name', 'oppName','result', 'blackWin']
            self.tbrrSummary['wins'] = 1 * (self.tbrrSummary.result == 1)

            tmpScores = self.tbrrSummary.groupby(['name']).agg(
                score = ('result','sum')).reset_index() # df[name, score]

            #add SB tiebreak, move sort values code to this df
            self.tbrrSummary['sbPoints'] = 0
            for idx, row in self.tbrrSummary.iterrows():
                self.tbrrSummary.at[idx, 'sbPoints'] = row.result * tmpScores.loc[tmpScores.name == row.oppName, 'score'].values[0]


            self.tbrrSummary = self.tbrrSummary.groupby(['name']).agg(
                score = ('result','sum'),
                sb = ('sbPoints', 'sum'),
                wins = ('wins','sum'),
                blackWins = ('blackWin','sum'),
                ).sort_values(by = ['score', 'sb', 'wins', 'blackWins'], ascending = False).reset_index()
            
            self.winner = self.tbrrSummary.name[0]

        else: raise Exception("Something went wrong; there shouldn't have been a tiebreak")  

    def simNorway(self):
        self.createGames()
        self.simRR()
        self.tie = 0
        if not hasattr(self, 'winner'):
            self.ties()
            self.tie = 1
        if not hasattr(self, 'winner'):
            print('something is broken, there is no winner after stage 3 is over')
        # print(self.games)
        #update player Elos
        self.newElo = {}
        for _, player in self.players.items(): #(key, value)
            player.updateRatings()
            self.newElo[player.name] = player.EloC
        self.magnus = self.players['Carlsen'].EloC

'''
    def createGames(self):

        rrGames = list(itertools.combinations(self.playerNames, 2))
        switchSides = [(x[1], x[0]) for x in rrGames]
        rrGames.extend(switchSides)
        rrGames.sort()
        self.games = pd.DataFrame([[game[0], game[1]] for game in rrGames], columns = ['whitePlayer', 'blackPlayer'])

    def simRR(self):
        #https://handbook.fide.com/files/handbook/Regulations_for_the_FIDE_Candidates_Tournament_2022.pdf
        self.games['format'] = 'c'
        self.games['stage'] = 'rr'
        self.games['played'] = 0
        self.games['result'] = 0

        for idx, row in self.games.iterrows():
            whitePlayer = self.players[row.whitePlayer]
            blackPlayer = self.players[row.blackPlayer]

            self.games.at[idx, 'played'] = 1
            result = playChess(bst, whitePlayer, blackPlayer, format = 'c') #points white player scored

            #TODO should I use the update ratings function or not?
            self.games.at[idx, 'result'] = result
        
        whiteResults = self.games[['whitePlayer', 'result']].values
        blackResults = self.games[['blackPlayer', 'result']].values
        blackResults[:, 1] = 1 - blackResults[:, 1] # to change the game results to black player POV
        
        self.rrSummary = pd.DataFrame(np.concatenate(
            (whiteResults, blackResults)
            , axis = 0))
        self.rrSummary.columns = ['name', 'result']
        self.rrSummary['wins'] = 1 * (self.rrSummary.result == 1)
        self.rrSummary = self.rrSummary.groupby(['name']).agg(
             score = ('result','sum'),
             wins = ('wins','sum'),
             ).sort_values(by = ['score', 'wins'], ascending = False).reset_index()
        self.rrSummary['first'] = 1 * (self.rrSummary.score == max(self.rrSummary.score))

        self.remaining = list(self.rrSummary[self.rrSummary['first'] == 1].name)
        if len(self.remaining) == 1:
            self.winner = self.remaining[0]

    def tieS12(self):

        if 's1' in self.games.stage.unique():
            stage = 's2'
        else: stage = 's1'

        s1Players = self.remaining       
        if len(s1Players) == 1:
            self.winner = s1Players[0]
        if len(s1Players) > 1:
            if len(s1Players) == 2:
                player1 = self.players[s1Players[0]]
                player2 = self.players[s1Players[1]]

                if stage == 's1':
                    game1 = playChess(bst, player1, player2, format = 'r') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player1.name, player2.name, 'r', 's1', 1, game1]

                    game2 = playChess(bst, player2, player1, format = 'r') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player2.name, player1.name, 'r', 's1', 1, game2]

                elif stage == 's2':
                    game1 = playChess(bst, player1, player2, format = 'b') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player1.name, player2.name, 'b', 's2', 1, game1]

                    game2 = playChess(bst, player2, player1, format = 'b') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player2.name, player1.name, 'b', 's2', 1, game2]

                player1Score = game1 + (1 - game2)

                if player1Score > 1:
                    self.winner = player1.name
                elif player1Score == 1:
                    pass #move to s2 because remaining players will be > 1
                elif player1Score < 1:
                    self.winner = player2.name

                # print(s1Players)
            if len(s1Players) > 2:
                s1Games = list(itertools.combinations(self.remaining, 2))
                random.shuffle(s1Games)
                white = {name: 0 for name in self.remaining} #to track how many white games each player has
                rrGames = []
                for i, j in s1Games:
                    if white[i] > white[j]:
                        white[j] += 1
                        rrGames.append((j, i))
                    elif white[i] < white[j]:
                        white[i] += 1
                        rrGames.append((i, j))
                    elif white[i] == white[j]:
                        k = random.randint(0, 1)
                        if k == 0:
                            white[i] += 1
                            rrGames.append((i, j))
                        if k == 1:
                            white[j] += 1
                            rrGames.append((j, i))
                
                games = pd.DataFrame([[game[0], game[1]] for game in rrGames], columns = ['whitePlayer', 'blackPlayer'])

                games['format'] = 'r'
                games['stage'] = stage
                games['played'] = 0
                games['result'] = 0

                for idx, row in games.iterrows():
                    whitePlayer = self.players[row.whitePlayer]
                    blackPlayer = self.players[row.blackPlayer]

                    games.at[idx, 'played'] = 1
                    if stage == 's1':
                        result = playChess(bst, whitePlayer, blackPlayer, format = 'r') #points white player scored
                    elif stage == 's2':
                        result = playChess(bst, whitePlayer, blackPlayer, format = 'r') #points white player scored

                    #TODO should I use the update ratings function or not?
                    games.at[idx, 'result'] = result
                
                self.games = pd.concat([self.games, games], ignore_index = True, axis = 0)

                whiteResults = games[['whitePlayer', 'result']].values
                blackResults = games[['blackPlayer', 'result']].values
                blackResults[:, 1] = 1 - blackResults[:, 1] # to change the game results to black player POV

                self.rrSummary = pd.DataFrame(np.concatenate(
                    (whiteResults, blackResults)
                    , axis = 0))
                self.rrSummary.columns = ['name', 'result']
                self.rrSummary['wins'] = 1 * (self.rrSummary.result == 1)
                self.rrSummary = self.rrSummary.groupby(['name']).agg(
                    score = ('result','sum'),
                    wins = ('wins','sum'),
                    ).sort_values(by = ['score', 'wins'], ascending = False).reset_index()
                self.rrSummary['first'] = 1 * (self.rrSummary.score == max(self.rrSummary.score))

                self.remaining = list(self.rrSummary[self.rrSummary['first'] == 1].name)
                if len(self.remaining) == 1:
                    self.winner = self.remaining[0]


    def tieS3(self): #janky knockout tournament code that seems to work pretty well!
        random.shuffle(self.remaining)
        while len(self.remaining) > 1:
            losers = []
            for j in range(0, len(self.remaining), 2):

                if len(self.remaining) == j + 1:
                    continue #this person gets a bye

                games = pd.DataFrame([[self.remaining[j], self.remaining[j+1]]], columns = ['whitePlayer', 'blackPlayer'])

                games['format'] = 'b'
                games['stage'] = 's3'
                games['played'] = 0
                games['result'] = 0

                for idx, row in games.iterrows(): #loop is not necessary because we only have 1 row... easy to just leave as is for now
                    whitePlayer = self.players[row.whitePlayer]
                    blackPlayer = self.players[row.blackPlayer]

                    games.at[idx, 'played'] = 1
                    result = playChess(bst, whitePlayer, blackPlayer, format = 'b') #points white player scored

                    if result == 1: 
                        loser = blackPlayer.name
                    elif result < 1: #technically, if it's a draw the game should be replayed and colors swapped, but this is good enough
                        loser = whitePlayer.name
                    losers.append(loser)

                    games.at[idx, 'result'] = result
                
                self.games = pd.concat([self.games, games], ignore_index = True, axis = 0)

            for loser in losers:
                self.remaining.remove(loser)
            
        if len(self.remaining) == 1:
            self.winner = self.remaining[0]
        elif not hasattr(self, 'winner'): 
            print(self.remaining)
            raise Exception("Something is broke. S3 ended without a winner")

    def simCandidates(self):
        self.createGames()
        self.simRR()
        self.tie = 0
        if not hasattr(self, 'winner'):
            self.tieS12()
            self.tie = 1
            if not hasattr(self, 'winner'):
                self.tieS12()
                if not hasattr(self, 'winner'):
                    self.tieS3()
            # print(self.rrSummary)
        if not hasattr(self, 'winner'):
            print('something is broken, there is no winner after stage 3 is over')


# tournament = Candidates(getCandidates())
# tournament.simCandidates()

'''