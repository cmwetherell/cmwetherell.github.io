import chess.pgn
import requests
import json
import pandas as pd
import math
import plotly.express as px
import argparse
import os


def fetch_game_analysis(pgn_data):
    """
    Fetches game analysis from the API for a given PGN string.

    Parameters:
        pgn_data (str): The PGN data of the game to be analyzed.

    Returns:
        dict: The JSON response from the API containing the game analysis.
    """
    url = 'https://elocator.fly.dev/analyze-game/'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'pgn': pgn_data})
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def calculate_accuracy_by_color(centipawn_evaluations):
    """
    Calculates the accuracy of moves for White and Black based on centipawn evaluations.

    Parameters:
        centipawn_evaluations (list): A list of centipawn evaluations before each move.

    Returns:
        tuple: Two lists containing accuracy values for White and Black respectively.
    """
    def centipawn_to_win_percent(centipawns):
        return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * centipawns)) - 1)

    win_percents = [centipawn_to_win_percent(cp) for cp in centipawn_evaluations]
    accuracies_white, accuracies_black = [], []

    for i in range(0, len(win_percents) - 1, 2):  # White's moves
        if i + 1 < len(win_percents):
            diff = abs(win_percents[i] - win_percents[i + 1])
            accuracies_white.append(103.1668 * math.exp(-0.04354 * diff) - 3.1669)

    for i in range(1, len(win_percents) - 1, 2):  # Black's moves
        if i + 1 < len(win_percents):
            diff = abs(win_percents[i] - win_percents[i + 1])
            accuracies_black.append(103.1668 * math.exp(-0.04354 * diff) - 3.1669)

    return accuracies_white, accuracies_black


def analyze_pgn_file(pgn_file, json_file, force_recreate=False):
    """
    Analyzes the games in a PGN file and saves results to a JSON file.

    Parameters:
        pgn_file (str): The path to the PGN file containing chess games.
        json_file (str): The path to save the analysis results in JSON format.
        force_recreate (bool): Whether to forcefully recreate the JSON file.

    Returns:
        pd.DataFrame: DataFrame containing summarized game analysis.
    """
    if os.path.exists(json_file) and not force_recreate:
        print(f"Using existing JSON file: {json_file}")
        with open(json_file, 'r') as file:
            analysis_results = json.load(file)
    else:
        print(f"Analyzing PGN file: {pgn_file}")
        analysis_results = []
        with open(pgn_file) as pgn:
            game = chess.pgn.read_game(pgn)
            while game:
                game_pgn = str(game)
                analysis_data = fetch_game_analysis(game_pgn)
                if analysis_data:
                    analysis_results.append(analysis_data)
                game = chess.pgn.read_game(pgn)

        with open(json_file, 'w') as file:
            json.dump(analysis_results, file)
        print(f"Saved analysis results to {json_file}")

    # Process analysis results into a DataFrame
    games_data = []
    for game in analysis_results[:11]:
        moves = game['positionAnalysis']
        eval_list = [move['evaluation'] for move in moves]
        white_moves = [move['complexity'] for i, move in enumerate(moves) if i % 2 == 0]
        black_moves = [move['complexity'] for i, move in enumerate(moves) if i % 2 != 0]

        white_accuracy, black_accuracy = calculate_accuracy_by_color(eval_list)

        games_data.append({
            'whitePlayer': game['gameHeaders']['White'],
            'blackPlayer': game['gameHeaders']['Black'],
            'round': game['gameHeaders']['Round'],
            'overallComplexity': sum(white_moves + black_moves) / len(white_moves + black_moves),
            'whiteComplexity': sum(white_moves) / len(white_moves),
            'blackComplexity': sum(black_moves) / len(black_moves),
            'whiteAccuracy': sum(white_accuracy) / len(white_accuracy),
            'blackAccuracy': sum(black_accuracy) / len(black_accuracy),
        })
    
    df = pd.DataFrame(games_data)
    
    # sort by overall complexity in place, highest complexity on top
    df.sort_values(by='overallComplexity', ascending=False, inplace=True)

    # Display the DataFrame
    print(df.to_markdown(index=False, floatfmt=".3f"))

    return pd.DataFrame(games_data)


def create_visualizations(games_df):
    """
    Creates and displays visualizations for the analyzed chess games.

    Parameters:
        games_df (pd.DataFrame): DataFrame containing the analyzed games data.
    """
    # Complexity vs Accuracy Scatter Plot
    modified_data = []
    for _, row in games_df.iterrows():
        modified_data.append({'Player': row['whitePlayer'], 'Complexity': row['whiteComplexity'], 'Accuracy': row['whiteAccuracy']})
        modified_data.append({'Player': row['blackPlayer'], 'Complexity': row['blackComplexity'], 'Accuracy': row['blackAccuracy']})

    modified_df = pd.DataFrame(modified_data)
    fig1 = px.scatter(modified_df, x='Complexity', y='Accuracy', trendline='ols', title='Complexity vs Accuracy')
    fig1.update_layout(template='simple_white')
    fig1.show()

    # Overall Complexity Line Plot
    fig2 = px.line(games_df, y='overallComplexity', title='Overall Complexity of Each Game', labels={'index': 'Round', 'overallComplexity': 'Overall Complexity'})
    fig2.update_layout(template='simple_white')
    fig2.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze chess games from a PGN file.")
    parser.add_argument("pgn_file", type=str, help="Path to the PGN file.")
    parser.add_argument("json_file", type=str, help="Path to save or load the JSON analysis file.")
    parser.add_argument("--force", action="store_true", help="Force recreation of the JSON file.")

    args = parser.parse_args()

    # Analyze the PGN file
    games_df = analyze_pgn_file(args.pgn_file, args.json_file, force_recreate=args.force)

    # Display visualizations
    create_visualizations(games_df)
