from math import remainder
import pandas as pd
import pickle
from player import Player
import numpy as np
import itertools
import lightgbm as lgb
import random

def getCandidates():
    candidates = pickle.load(open( "./chessSim/data/playerData.p", "rb" ) )
    candidates = candidates[candidates.Name.isin(
        ['Nakamura, Hikaru',
         'Caruana, Fabiano',
         'Giri, Anish',
         'Praggnanandhaa R',
         'Wei, Yi',
         'Sindarov, Javokhir',
         'Esipenko, Andrey',
         'Bluebaum, Matthias'
         ])]
    candidates = {x[0]: Player(x[0], x[1], x[2] , x[3]) for x in np.array(candidates)}
    # Fallback ratings (FIDE Mar 2026) for players not found in scraped data
    fallbacks = {
        'Nakamura, Hikaru': (2810, 2742, 2838),
        'Caruana, Fabiano': (2795, 2727, 2769),
        'Giri, Anish': (2753, 2689, 2666),
        'Praggnanandhaa R': (2741, 2663, 2698),
        'Wei, Yi': (2754, 2726, 2698),
        'Sindarov, Javokhir': (2745, 2727, 2662),
        'Esipenko, Andrey': (2698, 2657, 2652),
        'Bluebaum, Matthias': (2698, 2587, 2634),
    }
    for name, (c, r, b) in fallbacks.items():
        if name not in candidates:
            candidates[name] = Player(name, c, r, b)

    return candidates

def getWomenCandidates():
    candidates = pickle.load(open( "./chessSim/data/playerDataWomen.p", "rb" ) )
    candidates = candidates[candidates.Name.isin(
        ['Zhu, Jiner',
          'Muzychuk, Anna',
          'Goryachkina, Aleksandra',
          'Tan, Zhongyi',
          'Lagno, Kateryna',
          'Deshmukh, Divya',
          'Assaubayeva, Bibisara',
          'Rameshbabu, Vaishali'
          ])]
    candidates = {x[0]: Player(x[0], x[1], x[2] , x[3]) for x in np.array(candidates)}
    # Fallback ratings (FIDE Mar 2026) for players not found in scraped data
    fallbacks = {
        'Zhu, Jiner': (2578, 2479, 2411),
        'Muzychuk, Anna': (2522, 2398, 2400),
        'Goryachkina, Aleksandra': (2534, 2499, 2424),
        'Tan, Zhongyi': (2535, 2502, 2424),
        'Lagno, Kateryna': (2508, 2435, 2414),
        'Deshmukh, Divya': (2497, 2416, 2351),
        'Assaubayeva, Bibisara': (2516, 2439, 2457),
        'Rameshbabu, Vaishali': (2470, 2387, 2371),
    }
    for name, (c, r, b) in fallbacks.items():
        if name not in candidates:
            candidates[name] = Player(name, c, r, b)

    return candidates

bst = lgb.Booster(model_file = './chessSim/models/model.txt')
_bst_iteration = bst.best_iteration

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-10, 11, 5)

    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=_bst_iteration).mean(axis = 0).tolist()
    result = np.random.choice([0,0.5,1], p=preds)

    return result

def batchPredict(model, whiteElos, blackElos):
    """Predict outcomes for multiple games at once. Returns array of results (0, 0.5, 1)."""
    n = len(whiteElos)
    avgRange = range(-10, 11, 5)
    n_avg = len(avgRange)

    # Build feature matrix for all games × all variations
    rows = []
    for j in range(n):
        for i in avgRange:
            rows.append([whiteElos[j] - i, blackElos[j] - i, whiteElos[j] - blackElos[j],
                        ((whiteElos[j] - i) + (blackElos[j] - i)) / 2])

    all_preds = model.predict(rows, num_iteration=_bst_iteration)  # single batch call
    # Reshape to (n_games, n_avg, 3) and average across variations
    all_preds = all_preds.reshape(n, n_avg, 3).mean(axis=1)

    # Sample outcomes for all games at once
    results = np.empty(n)
    choices = np.array([0, 0.5, 1])
    for j in range(n):
        results[j] = np.random.choice(choices, p=all_preds[j])
    return results

def playChess(model, whitePlayer, blackPlayer, format):

    whiteElo = getattr(whitePlayer, 'Elo' + format.upper())
    blackElo = getattr(blackPlayer, 'Elo' + format.upper())

    result = chessMLPred(model, whiteElo, blackElo)
    whitePlayer.addGame(result, whiteElo, blackElo, format)
    blackPlayer.addGame((1 - result), blackElo, whiteElo, format)

    return result

def second_largest(list_input):
    # print(list_input)
    # print(type(list_input))
    return list(list_input.sort_values(ascending=False))[-2]

class Candidates:
    
    def __init__(self, players, games = None):
        self.players = players.copy()
        self.playerNames = players.keys()
        if games is not None:
            self.games = games.copy()
        else:
            self.games = None
        self.loadGames = self.games != None
        self.dingSecond = 0

    def createGames(self):

        rrGames = list(itertools.combinations(self.playerNames, 2))
        switchSides = [(x[1], x[0]) for x in rrGames]
        rrGames.extend(switchSides)
        rrGames.sort()
        self.games = pd.DataFrame([[game[0], game[1]] for game in rrGames], columns = ['whitePlayer', 'blackPlayer'])

        self.games['format'] = 'c'
        self.games['stage'] = 'rr'
        self.games['played'] = 0
        self.games['result'] = 0.0
        

        self.games.to_csv("./chessSim/data/candidatesGames2026.csv", index=False)
        # self.games.to_csv("./chessSim/data/womensCandidatesGames2026.csv", index=False)

    def simRR(self):
        #https://handbook.fide.com/files/handbook/Regulations_for_the_FIDE_Candidates_Tournament_2024.pdf
        self.games['blackWin'] = 0

        # Batch predict all unplayed games at once
        unplayed = self.games[self.games.played == 0]
        if len(unplayed) > 0:
            whiteElos = np.array([self.players[wp].EloC for wp in unplayed.whitePlayer])
            blackElos = np.array([self.players[bp].EloC for bp in unplayed.blackPlayer])
            results = batchPredict(bst, whiteElos, blackElos)

            # Update games and player objects
            for i, (idx, row) in enumerate(unplayed.iterrows()):
                result = results[i]
                self.games.at[idx, 'played'] = 1
                self.games.at[idx, 'result'] = result
                wp = self.players[row.whitePlayer]
                bp = self.players[row.blackPlayer]
                wp.addGame(result, wp.EloC, bp.EloC, 'c')
                bp.addGame((1 - result), bp.EloC, wp.EloC, 'c')

        whiteResults = self.games[['whitePlayer', 'blackPlayer', 'result', 'blackWin']].values
        blackResults = self.games[['blackPlayer', 'whitePlayer', 'result', 'blackWin']].values
        blackResults[:, 2] = 1 - blackResults[:, 2] # to change the game results to black player POV
        blackResults[:, 3] = 1 * (blackResults[:, 2] == 1) #checking for black wins, used for tb

        self.tbrrSummary = pd.DataFrame(np.concatenate(
            (whiteResults, blackResults)
            , axis = 0))
        self.tbrrSummary.columns = ['name', 'oppName','result', 'blackWin']
        self.tbrrSummary['wins'] = 1 * (self.tbrrSummary.result == 1)

        tmpScores = self.tbrrSummary.groupby(['name']).agg(
            score = ('result','sum')).reset_index() # df[name, score]

        # SB tiebreak: vectorized via merge instead of row-by-row apply
        self.tbrrSummary = self.tbrrSummary.merge(
            tmpScores.rename(columns={'name': 'oppName', 'score': 'oppScore'}), on='oppName')
        self.tbrrSummary['sbPoints'] = self.tbrrSummary['result'] * self.tbrrSummary['oppScore']
        self.tbrrSummary.drop(columns=['oppScore'], inplace=True)

        self.tbrrSummary = self.tbrrSummary.groupby(['name']).agg(
            score = ('result','sum'),
            sb = ('sbPoints', 'sum'),
            wins = ('wins','sum'),
            blackWins = ('blackWin','sum'),
            ).reset_index()

        self.tbrrSummary = self.tbrrSummary.sort_values(by = ['score', 'sb', 'wins', 'blackWins'], ascending = False).reset_index()

        self.tbrrSummary['first'] = 1 * (self.tbrrSummary.score == max(self.tbrrSummary.score))
        self.winScore = max(self.tbrrSummary.score)



        self.remaining = list(self.tbrrSummary[self.tbrrSummary['first'] == 1].name)
        if len(self.remaining) == 1:
            self.winner = self.remaining[0]

        self.second = list(self.tbrrSummary.name)[1] #Gets second entry of sorted names based on FIDE regulations TB criteria, overwritten later if there is TBs TODO Not perfect. At least SB is first TB.

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
                    self.games.loc[self.games.shape[0]] = [player1.name, player2.name, 'r', 's1', 1, game1, 1*(game1==0)]

                    game2 = playChess(bst, player2, player1, format = 'r') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player2.name, player1.name, 'r', 's1', 1, game2, 1*(game1==0)]

                elif stage == 's2':
                    game1 = playChess(bst, player1, player2, format = 'b') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player1.name, player2.name, 'b', 's2', 1, game1, 1*(game1==0)]

                    game2 = playChess(bst, player2, player1, format = 'b') #points white player scored
                    self.games.loc[self.games.shape[0]] = [player2.name, player1.name, 'b', 's2', 1, game2, 1*(game1==0)]

                player1Score = game1 + (1 - game2)

                if player1Score > 1:
                    self.winner = player1.name
                    self.second = player2.name
                elif player1Score == 1:
                    pass #move to s2 because remaining players will be > 1
                elif player1Score < 1:
                    self.winner = player2.name
                    self.second = player1.name

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
                games['result'] = 0.0

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
                    self.rrSummary['second'] = 1 * (self.rrSummary.score == second_largest(self.rrSummary.score))
                    self.secondList = list(self.rrSummary[self.rrSummary['second'] == 1].name)
                    if len(self.secondList) == 1:
                        self.second = self.secondList[0]


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
                games['result'] = 0.0

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
                    self.second = loser # last loser is second place
                    games.at[idx, 'result'] = result
                
                self.games = pd.concat([self.games, games], ignore_index = True, axis = 0)

            for loser in losers:

                self.remaining.remove(loser)
            
        if len(self.remaining) == 1:
            self.winner = self.remaining[0]
        elif not hasattr(self, 'winner'): 
            print(self.remaining)
            raise Exception("Something is broke. S3 ended without a winner")
        
    def generateGameId(self, whitePlayer, blackPlayer):
        # Generates a game ID using the first 3 letters of the player names
        return whitePlayer[:3] + '|' + blackPlayer[:3]

    def convertSimToJSON(self):
        # Filter to round-robin games only
        rr = self.games[self.games['stage'] == 'rr']

        # Vectorized game ID generation + list comprehension (no iterrows)
        wp = rr['whitePlayer'].values
        bp = rr['blackPlayer'].values
        results = rr['result'].values
        games_list = [
            {"gameId": w[:3] + '|' + b[:3], "outcome": r, "whitePlayer": w, "blackPlayer": b}
            for w, b, r in zip(wp, bp, results)
        ]

        self.result_json = {
            "winner": self.winner,
            "second": self.second,
            "tie": self.tie,
            "games": games_list
        }

    def simCandidates(self):
        if self.games is None:
            self.createGames()
        self.simRR()
        self.tie = 0
        if not hasattr(self, 'winner'):
            self.tieS12()
            self.tie = 1
            # print("TIE")
            if not hasattr(self, 'winner'):
                self.tieS12()
                if not hasattr(self, 'winner'):
                    self.tieS3()
        if hasattr(self, 'winner'):
            self.convertSimToJSON()
        # print(self.winner)
            # print(self.rrSummary)
        # if self.winner == 'Radjabov':
        #     print(self.tbrrSummary)
        if not hasattr(self, 'winner'):
            print('something is broken, there is no winner after stage 3 is over')
        if not hasattr(self, 'second'):
            print('something is broken, there is no second after stage 3 is over')
            print(self.games)
            print(self.tbrrSummary)

if __name__ == "__main__":
    tournament = Candidates(getCandidates())
    tournament.simCandidates()