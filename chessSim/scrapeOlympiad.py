import requests
import pandas as pd
import pickle

#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

def splitRating(string):
    if '.' in str(string):
        return int(str(string).rpartition('.')[0])
    elif ' ' in str(string):
        return int(str(string).rpartition(' ')[0])
    else: raise Exception('Unexpected format for names')

def splitName(string):
    if ' ' in string:
        tmp = string.rpartition(' ')[0]
        if ' ' in tmp:
            return tmp.rpartition(' ')[0].rstrip()
    else: raise Exception('Unexpected format for names')

def main():

    # playersURL = 'http://chess-results.com/tnr368908.aspx?lan=1&art=16&flag=30&zeilen=99999'
    # tables = pd.read_html(requests.get(playersURL, verify = False,
    #                                 headers={'User-agent': 'Mozilla/5.0'}).text)
    # players = tables[3]
    # players.columns = players.iloc[0]
    # players = players.drop(players.index[0])
    # print(players)

    roundResultsURL = 'http://chess-results.com/tnr368908.aspx?lan=1&art=3&rd=1&flag=30&zeilen=99999'
    tables = pd.read_html(requests.get(roundResultsURL, verify = False,
                                headers={'User-agent': 'Mozilla/5.0'}).text)
    print(tables[3].iloc[2])

    # playerData = tables[0].loc[:,["Name", "Classic", "Rapid", "Blitz"]]

    # playerData.Classic = playerData.Classic.apply(splitRating)
    # playerData.Rapid = playerData.Rapid.apply(splitRating)
    # playerData.Blitz = playerData.Blitz.apply(splitRating)
    # playerData.Name = playerData.Name.apply(splitName)

    # # print(playerData)

    # pickle.dump(playerData, open( "./chessSim/data/playerData.p", "wb" ) )
if __name__=="__main__":
    main()
