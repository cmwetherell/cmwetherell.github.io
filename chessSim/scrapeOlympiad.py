import requests
import pandas as pd
import pickle
import numpy as np
import chess.pgn # I would normally do 'from chess import pgn', but the developer examples did it this way.

#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

def getTeamRating(team, players):
    avgRating = players.Rtg[players.Team == team].sort_values(ascending = False).head(4).mean()
    fifthRating = 0
    if players.Rtg[players.Team == team].shape[0] > 4:
        # print(players.Rtg[players.Team == team].sort_values(ascending = False).reset_index())
        fifthRating = players.Rtg[players.Team == team].sort_values(ascending = False).reset_index(drop = True).iloc[4] #get reserve rating

    return pd.Series([avgRating, fifthRating])

def whiteGames(gamesWhite, teams):

    gamesWhite = gamesWhite[gamesWhite.board == 1].whiteTeam.value_counts().to_frame().reset_index()
    gamesWhite.columns = ['team', ' whiteCount']
    teamsWhite = teams.merge(gamesWhite)

    return teamsWhite

def main():

    # get Olympiad players

    playersURL = 'http://chess-results.com/tnr653631.aspx?lan=1&art=16&flag=30&zeilen=99999'
    
    players = pd.read_html(requests.get(playersURL, verify = False,
                                    headers={'User-agent': 'Mozilla/5.0'}).text)

    players = players[4]
    players.columns = players.iloc[0]
    players = players.drop(players.index[0])
    # print(players)
    players.loc[players['rtg+/-'].isnull(), 'rtg+/-'] = 0
    players.Rtg = players.Rtg.astype(int)
    players['dR'] = players['rtg+/-'].astype(int) / 10
    players.loc[players.Rtg==0, 'Rtg'] = players.Rp.astype(int)
    players.loc[players.Rtg==0, 'Rtg'] = 1200
    players.Rtg = round(players.Rtg + players['dR']).astype(int)
    # players.Rtg = players.Rp
    players.to_csv('./chessSim/data/olympiad/players2022.csv', index = False)
    # print(players)
    
    # make teams
    teamURL = 'http://chess-results.com/tnr653631.aspx?lan=1&art=32&turdet=YES&flag=30&zeilen=99999'

    teams = pd.read_html(requests.get(teamURL, verify = False,
                                    headers={'User-agent': 'Mozilla/5.0'}).text)


    teams = teams[6]

    teams.columns = teams.iloc[0]
    teams = teams.drop(teams.index[0])
    # teams = teams.drop(teams.index[0])
    teams = teams[['No.', 'Team']]
    teams.columns = ['initRank', 'short', 'team']
    teams = teams[['team', 'initRank']]

    # teams[['avgRating', 'fifthRating']] = teams.team.apply(getTeamRating, players = players)
    # teams = teams.sort_values(by = ['avgRating', 'fifthRating'], ascending = False).reset_index(drop = True)

    # teams['initRank'] = teams.index + 1
    teams['mp'], teams['IS10'], teams['gp'], teams['oppMP10'] = 0,0,0,0

    invalidTeams = ['Pakistan', 'Cote d\'Ivoire', 'Rwanda', 'Lesotho']
    teams = teams[~teams['team'].isin(invalidTeams)]

    teams.to_csv('./chessSim/data/olympiad/teams2022.csv', index = False)

    # print(teams)

    #Process games from chess-results: http://chess-results.com/partieSuche.aspx?lan=1&art=4&tnr=368908&rd=1
    pgn = open("./chessSim/data/olympiad/2022.pgn") # http://caissabase.co.uk/ download Scid files, export to pgn

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
    # print(df['round'].unique())
    df['round'] = df['round'].astype(float).apply(np.floor)

    df.loc[df.result=='1-0', 'result'] = 1 #use integers for multiclass indexes
    df.loc[df.result=='1/2-1/2', 'result'] = 0.5
    df.loc[df.result=='0-1', 'result'] = 0

    df.loc[df.whiteElo==0, 'whiteElo'] = 1700 ### using TPR of unranked players in 2018 Olympiad.
    df.loc[df.blackElo==0, 'blackElo'] = 1700

        ##Feature Engineering (very simple!)
    df['EloDiff'] = df.whiteElo - df.blackElo
    df['EloAvg'] =((df.whiteElo + df.blackElo) / 2 ).astype(int)


    # print(df)
    # write to csv for future use
    df.to_csv('./chessSim/data/olympiad/games2022.csv', index = False)
    # print(df.columns)

    rounds = ['https://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=1&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=2&flag=30',
            'https://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=3&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=4&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=5&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=6&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=7&flag=30',
            'http://chess-results.com/tnr653631.aspx?lan=1&art=2&rd=8&flag=30',
    ]

    i = 1
    matchResults = []
    for roundURL in rounds:


        roundResults = pd.read_html(requests.get(roundURL, verify = False,
                                        headers={'User-agent': 'Mozilla/5.0'}).text)


        roundResults = roundResults[4]
        roundResults.columns = roundResults.iloc[1]
        roundResults = roundResults.drop(roundResults.index[0])
        roundResults = roundResults.drop(roundResults.index[0])

        whiteTeams = roundResults.iloc[:, [4, 7, 12]]
        blackTeams = roundResults.iloc[:, [12, 9, 4]]
        # print(whiteTeams)

        whiteTeams.columns = ['playerTeam', 'gp', 'oppTeam']
        blackTeams.columns = ['playerTeam', 'gp', 'oppTeam']

        results = pd.concat([whiteTeams, blackTeams]).reset_index(drop=True)
        results['round'] = i
        i+=1

        results.gp = results.gp.replace('3½', '3.5')
        results.gp = results.gp.replace('2½', '2.5')
        results.gp = results.gp.replace('1½', '1.5')
        results.gp = results.gp.replace('½', '0.5')
        # print(results.gp)

        results.gp = results.gp.astype(float)

        # print(results)

        mpConditions = [
            (results.gp > 2),
            (results.gp == 2),
            (results.gp < 2),
        ]
        mpValues = [2,1,0]

        results['mp'] = np.select(mpConditions, mpValues)

        results.loc[results.playerTeam == 'India *)', 'playerTeam'] = 'India'
        results.loc[results.oppTeam == 'India *)', 'oppTeam'] = 'India'

        results = results[['playerTeam', 'oppTeam', 'round', 'gp']]

        invalidTeams = ['Pakistan',  'Rwanda', ]
        results = results[~results['playerTeam'].isin(invalidTeams)]  

        matchResults.append(results)

    matchResults = pd.concat(matchResults)
    matchResults.to_csv('./chessSim/data/olympiad/matches2022.csv', index = False)

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

# [Event "Chennai Chess Olympiad | Open"]
# [Site "chess24.com"]
# [Date "2022.07.29"]
# [Round "1"]
# [White "Vidit, Santosh Gujrathi"]
# [Black "Makoto, Rodwell"]
# [Result "1-0"]
# [Board "1"]
# [WhiteCountry "IND"]
# [WhiteFideId "5029465"]
# [WhiteElo "2714"]
# [WhiteTitle "GM"]
# [WhiteEloChange "1"]
# [BlackCountry "ZIM"]
# [BlackFideId "11000120"]
# [BlackElo "2346"]
# [BlackTitle "IM"]
# [BlackEloChange "-2"]