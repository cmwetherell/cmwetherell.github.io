import lightgbm as lgb
from sklearn.metrics import mean_squared_error, log_loss
import pandas as pd
import numpy as np

def main():

    print('Loading data...')
    # load or create your dataset
    df = pd.read_csv('./chess-sim/data/caissabase_df.csv')

    df.loc[df.result=='1-0', 'result'] = 2 #use integers for multiclass indexes
    df.loc[df.result=='1/2-1/2', 'result'] = 1
    df.loc[df.result=='0-1', 'result'] = 0
    df.result = df.result.astype(int)


    #create testing data for early stopping
    df_train = df.sample(frac = 0.7)
    df_test = df.drop(df_train.index)

    # create training input components
    y_train = df_train['result']
    y_test = df_test['result']
    X_train = df_train.drop('result', axis=1)
    X_test = df_test.drop('result', axis=1)

    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

    # specify your configurations as a dict
    # I didn't do much hyperparameter tuning, I don't think it's all that material for our purposes.
    params = { 
        'objective': 'multiclass',
        'metric': 'multi_logloss',
        'num_leaves': 300,
        'learning_rate': 0.05,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 1,
        # 'num_iterations': 10,
        'num_class': 3,
        'monotone_constraints': [0, 0, 1, 0] # white must score higher if they have a bigger advantage
    }

    print('Starting training...')
    # train
    gbm = lgb.train(params,
                    lgb_train,
                    num_boost_round=300, #best model had 2900 trees, but the added accuracy and complexity isn't worth the prediction time cost during the simulations
                    valid_sets=lgb_eval,
                    callbacks=[lgb.early_stopping(stopping_rounds=5)])

    print('Saving model...')
    # save model to file
    gbm.save_model('./chess-sim/models/model.txt')

    print('Starting predicting...')

    # predict
    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)

    # eval
    z = [i.index(max(i)) for i in y_pred.tolist()] # 0,1,2 if black wins, draw, white wins

    rmse_test = mean_squared_error(np.array(y_test) / 2, np.array(z) / 2) ** 0.5
    cross_entropy_test =  log_loss(y_test, y_pred)

    print(f'The RMSE of prediction is: {rmse_test}')
    print(f'The Cross Entropy of prediction is: {cross_entropy_test}')

if __name__ == "__main__":
    main()