import requests
import pandas as pd
import pickle

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
    else: raise Exception('Unexpected format for names')

def replace_nbsp(text):
    return text.replace('\xa0', ' ')

def main():

    url = 'https://www.2700chess.com/women'
    tables = pd.read_html(requests.get(url, verify = False,
                                    headers={'User-agent': 'Mozilla/5.0'}).text)
    
    playerData = tables[0].loc[:,["Name", "Classic", "Rapid", "Blitz"]]

    playerData.Classic = playerData.Classic.apply(splitRating)
    playerData.Rapid = playerData.Rapid.apply(splitRating)
    playerData.Blitz = playerData.Blitz.apply(splitRating)
    playerData.Name = playerData.Name.apply(replace_nbsp)

    pickle.dump(playerData, open( "./chessSim/data/playerDataWomen.p", "wb" ) )

if __name__=="__main__" or __name__=="scrape2700": #scrape2700 is the name of the script, importing it into another file will run the main function automatically.
    main()
