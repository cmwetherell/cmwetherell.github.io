import requests
import pandas as pd
import pickle
from io import StringIO



#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

def splitRating(string):
    if string == "unrat":
        return 2700
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
        else:
            return tmp
    else: raise Exception('Unexpected format for names')
    
def main():
    try:
        url = 'https://www.2700chess.com/'
        tables = pd.read_html(StringIO(requests.get(url, verify = False,
                                        headers={'User-agent': 'Mozilla/5.0'}).text))
        playerData = tables[0].loc[:,["Name", "Classical", "Rapid", "Blitz"]]

        # ranme classical to classic
        playerData.columns = ["Name", "Classic", "Rapid", "Blitz"]

        playerData.Classic = playerData.Classic.apply(splitRating)
        playerData.Rapid = playerData.Rapid.apply(splitRating)
        playerData.Blitz = playerData.Blitz.apply(splitRating)
        # playerData.Name = playerData.Name.apply(splitName)

        playerData.loc[playerData.Name == 'Ding', 'Name'] = 'Ding Liren'

        pickle.dump(playerData, open( "./chessSim/data/playerData.p", "wb" ) )
        
    except Exception as e:
        print(e)

if __name__=="__main__" or __name__=="scrape2700": #scrape2700 is the name of the script, importing it into another file will run the main function automatically.
    main()
