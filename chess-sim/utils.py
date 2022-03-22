from grandPrix import GrandPrix
import pandas as pd

def simGrandPrix(playerData, overridePool = False, gameData = None):

    GP3 = GrandPrix(playerData, 'event3', overridePool, gameData)
    GP3.simGP()

    finalStandings = pd.concat([playerData[(playerData.event2 == 1) & (playerData.event3 == 0)], GP3.players]).reset_index(drop = True)

    finalStandings['gpScore'] = 0
    finalStandings['event2Points'] = finalStandings['event2Points'].fillna(0)
    finalStandings['event3Points'] = finalStandings['event3Points'].fillna(0)
    finalStandings['gpScore'] = finalStandings.event1Points + finalStandings.event2Points + finalStandings.event3Points

    finalStandings.TF = 1*(finalStandings.event1Points == 13) + 1*(finalStandings.event2Points == 13) + 1*(finalStandings.event3Points == 13)
    finalStandings.TS = 1*(finalStandings.event1Points == 10) + 1*(finalStandings.event2Points == 10) + 1*(finalStandings.event3Points == 10)

    fs = finalStandings.sort_values(by = ['gpScore','TF', 'TS', 'GP', 'GW'], ascending = False).reset_index(drop = True)
    
    fs['Qualify'] = "DNQ"
    fs.loc[fs.Name == fs.Name[0], 'Qualify'] = "First"
    fs.loc[fs.Name == fs.Name[1], 'Qualify'] = "Second"

    return fs, GP3.gameData, pd.DataFrame(GP3.koGames, columns = ['whitePLayer', 'blackPlayer', 'result', 'koType'])