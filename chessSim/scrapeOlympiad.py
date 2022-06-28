import requests
import pandas as pd
import pickle
import chess.pgn # I would normally do 'from chess import pgn', but the developer examples did it this way.

#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

def main():

    # get Olympiad players

    playersURL = 'http://chess-results.com/tnr368908.aspx?lan=1&art=16&flag=30&zeilen=99999'
    players = pd.read_html(requests.get(playersURL, verify = False,
                                    headers={'User-agent': 'Mozilla/5.0'}).text)
    players = players[3]
    players.columns = players.iloc[0]
    players = players.drop(players.index[0])
    print(players)

    #TODO: make teams

    #Process games from chess-results: http://chess-results.com/partieSuche.aspx?lan=1&art=4&tnr=368908&rd=1
    pgn = open("./chessSim/data/olympiadGames/2018.pgn") # http://caissabase.co.uk/ download Scid files, export to pgn

    gameData = []
    while True:
        headers = chess.pgn.read_headers(pgn)
        if headers is None:
            break
        
        headerElements = [header for header in headers] #create list of meta data for each game, could be dict instead

        # if this criteria is met, the game has all the criteria we need for our model training data.
        if ('WhiteElo' in headerElements) & ('BlackElo' in headerElements) & ('Result' in headerElements) \
           & ('White' in headerElements) & ('Black' in headerElements) & ('WhiteTeam' in headerElements) & ('BlackTeam' in headerElements):

            # append relevant data to what will become our pandas df
            dat = [headers['White'], headers['WhiteTeam'], headers['WhiteElo'], \
                 headers['Black'], headers['BlackTeam'], headers['BlackElo'], headers['Result'] \
                     ,headers['Round'], headers['Board']]
            gameData.append(dat)
    df = pd.DataFrame(gameData, columns = ['whiteName', 'whiteTeam', 'whiteElo', 'blackName', 'blackTeam', 'blackElo', 'result', 'round', 'board'])

    ##Cleaning Data
    df = df[df.result != '*'] # cleaning some games that didn't have a valid result recorded
    df.whiteElo = df.whiteElo.astype(int) #changing type
    df.blackElo = df.blackElo.astype(int)

    df.loc[df.result=='1-0', 'result'] = 1 #use integers for multiclass indexes
    df.loc[df.result=='1/2-1/2', 'result'] = 0.5
    df.loc[df.result=='0-1', 'result'] = 0

    df.loc[df.whiteElo==0, 'whiteElo'] = 1700 ### using TPR of unranked players in 2018 Olympiad.
    df.loc[df.blackElo==0, 'blackElo'] = 1700

        ##Feature Engineering (very simple!)
    df['EloDiff'] = df.whiteElo - df.blackElo
    df['EloAvg'] =((df.whiteElo + df.blackElo) / 2 ).astype(int)

    print(df)
    # write to csv for future use
    df.to_csv('./chessSim/data/olympiadGames/2018.csv', index = False)

if __name__ == "__main__":
    main()



# Example game headers
# [Event "43rd Olympiad Batumi 2018 Open"]
# [Site "Batumi"]
# [Date "2018.09.24"]
# [Round "1"]
# [Board "1"]
# [White "So, Wesley"]
# [Black "Sanchez Alvarez, Roberto Carlos"]
# [Result "1-0"]
# [ECO "B90"]
# [WhiteElo "2776"]
# [BlackElo "2391"]
# [PlyCount "0"]
# [EventDate "2018.09.24"]
# [EventType "team"]
# [EventRounds "11"]
# [EventCountry "GEO"]
# [WhiteTeam "United States of America"]
# [BlackTeam "Panama"]