import numpy as np
import pandas as pd

class Player:
    
    def __init__(self, name, EloC, EloR , EloB):
        self.name = name
        self.EloC = EloC
        self.EloR = EloR
        self.EloB = EloB
        self.games = []
        self.fidePD = pd.read_csv('./chessSim/data/fidePD.csv')

    
    def addGame(self, result, myElo, opponentElo, format):
        newGame = [result, myElo, opponentElo, format]
        self.games.append(newGame)
    
    def calcChange(self, result, myElo, opponentElo, k):

            #get expected score pd https://www.fide.com/docs/regulations/FIDE%20Rating%20Regulations%202022.pdf
            ratingDiff = myElo - opponentElo
            absRD = abs(ratingDiff)
            favoriteInd = 1 if ratingDiff >= 0 else 0
            indexVal = self.fidePD[self.fidePD['diff'].gt(absRD)].index[0] #gets index from fide pd table with first value above rating difference
            expectedScore = self.fidePD.loc[indexVal, 'pd'] if favoriteInd == 1 else 1 - self.fidePD.loc[indexVal, 'pd']

            return (result - expectedScore) * k #k = 10 for GMs for C

    
    def updateRatings(self):

        for timeControl in ['c', 'r', 'b']:
            k = 10 if timeControl == 'c' else 20 #FIDE 'k' values for GMs in classical and rapid/blitz formats
            gamesTC = [row for row in self.games if row[3] == timeControl]    
            ratingChanges = [self.calcChange(result, myElo, opponentElo, k) for result, myElo, opponentElo, _ in gamesTC]
            ratingChange = sum(ratingChanges)
            tmpElo = getattr(self, 'Elo' + timeControl.upper())
            setattr(self,  'Elo' + timeControl.upper(), tmpElo + ratingChange)
            # if self.name == 'Carlsen':
            #     print(pd.DataFrame(gamesTC, ratingChanges), '\n', tmpElo, self.EloC)



'''

    def updateRating(self, oppRating, format, result, fidePD):
        if format == 'c':
            #get expected score pd https://www.fide.com/docs/regulations/FIDE%20Rating%20Regulations%202022.pdf
            ratingDiff = self.EloC - oppRating
            indexVal = fidePD[fidePD['diff'].gt(ratingDiff)].index[0] #gets index from fide pd table with first value above rating difference
            pd = fidePD.loc[indexVal, 'pd']

            self.EloC += (result - pd) * 10 #k = 10 for GMs for C

        if format == 'r':
            ratingDiff = self.EloR - oppRating
            indexVal = fidePD[fidePD['diff'].gt(ratingDiff)].index[0] 
            pd = fidePD.loc[indexVal, 'pd']

            self.EloR += (result - pd) * 20 #k = 20 for GMs for R and B

        if format == 'b':
            ratingDiff = self.EloB - oppRating
            indexVal = fidePD[fidePD['diff'].gt(ratingDiff)].index[0] 
            pd = fidePD.loc[indexVal, 'pd']

            self.EloB += (result - pd) * 20 #k = 20 for GMs for R and B

'''