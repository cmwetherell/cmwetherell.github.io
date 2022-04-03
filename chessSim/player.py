class Player:
    
    def __init__(self, name, EloC, EloR , EloB):
        self.name = name
        self.EloC = EloC
        self.EloR = EloR
        self.EloB = EloB
    
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



