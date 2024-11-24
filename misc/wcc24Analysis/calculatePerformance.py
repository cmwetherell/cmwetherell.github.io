import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from chessSim.player import Player

# Load the data
df = pd.read_csv('./misc/wcc24Analysis/fideGames.csv')

# Ensure correct data types
df['mmyy'] = pd.to_datetime(df['mmyy'], format='%m%y')

# Create a dictionary to store Player objects by name
players = {}

# Iterate through the DataFrame to populate Player objects
for _, row in df.iterrows():
    player_name = row['Player']

    if player_name not in players:
        # Create a new Player object for each unique player
        players[player_name] = Player(
            name=player_name,
            EloC=2500,  # Default Elo value, adjust as needed
            EloR=2500,
            EloB=2500
        )

        # Adjust Elo values for specific players
        if player_name == 'Ding Liren':
            players[player_name].EloC = 2728
        if player_name == 'Gukesh D':
            players[player_name].EloC = 2783

    # Add game details to the Player's record
    result = row['w']  # Result (1 for win, 0.5 for draw, 0 for loss)
    opponent_elo = row['opp_rating']  # Opponent's Elo rating
    game_format = 'c'
    player_elo = players[player_name].EloC

    players[player_name].addGame(result, player_elo, opponent_elo, game_format)

# calculate and print overall tpr for each player

for player_name, player_obj in players.items():
    tpr = player_obj.performance()
    print(f'{player_name}: {tpr:.2f}')

# Calculate TPR (Tournament Performance Rating) for each month
start_date = df['mmyy'].min()
end_date = pd.to_datetime('now')

dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # Monthly periods

tpr_data = []

for start_period in dates:
    for player_name, player_obj in players.items():
        # Filter games for the specific month
        filtered_games = [
            game for game, game_date in zip(player_obj.games, df[df['Player'] == player_name]['mmyy'])
            if game_date.month == start_period.month and game_date.year == start_period.year
        ]

        if not filtered_games:  # Skip if no games in this month
            continue

        # Temporarily replace games in Player object and calculate performance
        original_games = player_obj.games
        player_obj.games = filtered_games
        tpr = player_obj.performance()
        player_obj.games = original_games

        # Store TPR with player name and period
        tpr_data.append((player_name, start_period, tpr))

# Create a scatter plot for TPRs
plt.figure(figsize=(12, 8))

for player_name in players.keys():
    player_data = [(x[1], x[2]) for x in tpr_data if x[0] == player_name]
    if player_data:
        periods, tprs = zip(*player_data)
        plt.scatter(periods, tprs, label=player_name, alpha=0.7)

plt.xlabel('Time Preiod')
plt.ylabel('Tournament Performance Rating (TPR)')
plt.title('Monthly Tournament Performance Ratings (TPR)')
plt.legend()
plt.grid()
# save plt to file need to go up two directories and then assets/img/filename.png
plt.savefig('/Users/caleb/dev/pawnalyze-old-blog/docs/assets/img/wcc_tpr_24.png')

plt.show()


