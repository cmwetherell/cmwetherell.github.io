#TODO: I want to know what all the headers possible in the db are so I can do a better job preprocessing the data
import chess.pgn # I would normally do 'from chess import pgn', but the developer examples did it this way.
import pandas as pd

def main():
    pgn = open("./chess-sim/data/caissabase.pgn") # http://caissabase.co.uk/ download Scid files, export to pgn

    gameData = []
    while True:
        headers = chess.pgn.read_headers(pgn)
        if headers is None:
            break
        
        headerElements = [header for header in headers] #create list of meta data for each game, could be dict instead

        # if this criteria is met, the game has all the criteria we need for our model training data.
        if ('WhiteElo' in headerElements) & ('BlackElo' in headerElements) & ('Result' in headerElements):
            
            if ('Site' in headerElements) & ('INT' in headers['Site']):
                continue #skip internet games
            else:
                # append relevant data to what will become our pandas df
                dat = [headers['WhiteElo'], headers['BlackElo'], headers['Result']]
                gameData.append(dat)

    df = pd.DataFrame(gameData, columns = ['whiteElo', 'blackElo', 'result'])

    ##Cleaning Data
    df = df[df.result != '*'] # cleaning some games that didn't have a valid result recorded
    df.whiteElo = df.whiteElo.astype(int) #changing type
    df.blackElo = df.blackElo.astype(int)

    ##Feature Engineering (very simple!)
    df['EloDiff'] = df.whiteElo - df.blackElo
    df['EloAvg'] =((df.whiteElo + df.blackElo) / 2 ).astype(int)

    # write to csv for future use
    df.to_csv('./chess-sim/data/caissabase_df.csv', index = False)

if __name__ == "__main__":
    main()