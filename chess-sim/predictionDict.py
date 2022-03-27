import lightgbm as lgb
import pickle

bst = lgb.Booster(model_file = './chess-sim/models/model.txt')

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-5, 6, 5)
    
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=model.best_iteration).mean(axis = 0).tolist()
    # result = np.random.choice([0,0.5,1], p=preds) 

    return preds

def main():

    EloPairs = []

    for i in range(2500, 2901, 1):
        for j in range(2500, 2901, 1):
            EloPairs.append([i, j])
    
    preds = {(Elo[0], Elo[1]): chessMLPred(bst, Elo[0], Elo[1]) for Elo in EloPairs}

    pickle.dump(preds, open( "./chess-sim/models/preds.p", "wb" ) )

if __name__ == "__main__":
    main()
