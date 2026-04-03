"""
Round 5 statistics for 2026 FIDE Candidates Tournament blog post.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_URL = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DATABASE']}"
    f"?sslmode=require"
)

PLAYERS = {
    'Nak': 'Nakamura',
    'Car': 'Caruana',
    'Gir': 'Giri',
    'Pra': 'Praggnanandhaa',
    'Wei': 'Wei Yi',
    'Sin': 'Sindarov',
    'Esi': 'Esipenko',
    'Blu': 'Bluebaum',
}

STANDINGS = {
    'Sin': 3.5,
    'Car': 2.5,
    'Pra': 2.0,
    'Gir': 2.0,
    'Blu': 2.0,
    'Wei': 1.5,
    'Nak': 1.5,
    'Esi': 1.0,
}

print("Connecting to database...")
engine = create_engine(DB_URL)

print("Loading data...")
df = pd.read_sql("SELECT * FROM candidates_2026", engine)
print(f"Loaded {len(df):,} simulations\n")

# Get all game columns (contain "|")
game_cols = [c for c in df.columns if '|' in c]
print(f"Total game columns: {len(game_cols)}")

# Identify remaining (unplayed) games: ones with varying values
remaining_games = []
played_games = []
for col in game_cols:
    unique_vals = df[col].nunique()
    if unique_vals > 1:
        remaining_games.append(col)
    else:
        played_games.append(col)

print(f"Played games: {len(played_games)}")
print(f"Remaining games: {len(remaining_games)}")
print(f"\nPlayed games: {played_games}")
print(f"\nRemaining games: {remaining_games}")

# ============================================================
# 1. Win probability for each player
# ============================================================
print("\n" + "="*60)
print("1. WIN PROBABILITY (from 'winner' column)")
print("="*60)

n = len(df)
for code in ['Sin', 'Car', 'Pra', 'Gir', 'Blu', 'Wei', 'Nak', 'Esi']:
    name = PLAYERS[code]
    full_name = [k for k, v in {
        'Nakamura, Hikaru': 'Nak', 'Caruana, Fabiano': 'Car',
        'Giri, Anish': 'Gir', 'Praggnanandhaa R': 'Pra',
        'Wei, Yi': 'Wei', 'Sindarov, Javokhir': 'Sin',
        'Esipenko, Andrey': 'Esi', 'Bluebaum, Matthias': 'Blu',
    }.items() if v == code][0]

    wins = (df['winner'] == full_name).sum()
    pct = wins / n * 100
    print(f"  {name:20s}: {pct:6.2f}%  ({wins:,} / {n:,})")

# ============================================================
# 2. Win + 2nd place probability
# ============================================================
print("\n" + "="*60)
print("2. WIN + 2ND PLACE PROBABILITY")
print("="*60)

for code in ['Sin', 'Car', 'Pra', 'Gir', 'Blu', 'Wei', 'Nak', 'Esi']:
    name = PLAYERS[code]
    full_name = [k for k, v in {
        'Nakamura, Hikaru': 'Nak', 'Caruana, Fabiano': 'Car',
        'Giri, Anish': 'Gir', 'Praggnanandhaa R': 'Pra',
        'Wei, Yi': 'Wei', 'Sindarov, Javokhir': 'Sin',
        'Esipenko, Andrey': 'Esi', 'Bluebaum, Matthias': 'Blu',
    }.items() if v == code][0]

    wins = (df['winner'] == full_name).sum()
    seconds = (df['second'] == full_name).sum()
    total = wins + seconds
    pct_win = wins / n * 100
    pct_2nd = seconds / n * 100
    pct_total = total / n * 100
    print(f"  {name:20s}: Win {pct_win:6.2f}% + 2nd {pct_2nd:6.2f}% = Top2 {pct_total:6.2f}%")

# ============================================================
# 3. Tiebreak stats
# ============================================================
print("\n" + "="*60)
print("3. TIEBREAK STATISTICS")
print("="*60)

tie_pct = (df['tie'] == 1).sum() / n * 100
print(f"  Simulations with tiebreak: {tie_pct:.1f}%")
print(f"  Simulations without tiebreak: {100 - tie_pct:.1f}%")

print(f"\n  Win% WITH vs WITHOUT tiebreak per player:")
tie_sims = df[df['tie'] == 1]
no_tie_sims = df[df['tie'] == 0]
n_tie = len(tie_sims)
n_notie = len(no_tie_sims)

for code in ['Sin', 'Car', 'Pra', 'Gir', 'Blu', 'Wei', 'Nak', 'Esi']:
    name = PLAYERS[code]
    full_name = [k for k, v in {
        'Nakamura, Hikaru': 'Nak', 'Caruana, Fabiano': 'Car',
        'Giri, Anish': 'Gir', 'Praggnanandhaa R': 'Pra',
        'Wei, Yi': 'Wei', 'Sindarov, Javokhir': 'Sin',
        'Esipenko, Andrey': 'Esi', 'Bluebaum, Matthias': 'Blu',
    }.items() if v == code][0]

    win_with_tie = (tie_sims['winner'] == full_name).sum() / n_tie * 100 if n_tie > 0 else 0
    win_no_tie = (no_tie_sims['winner'] == full_name).sum() / n_notie * 100 if n_notie > 0 else 0
    print(f"  {name:20s}: No tiebreak {win_no_tie:6.2f}% | With tiebreak {win_with_tie:6.2f}%")

# ============================================================
# 4. Average winning score
# ============================================================
print("\n" + "="*60)
print("4. AVERAGE WINNING SCORE")
print("="*60)

# Compute each player's score per simulation
CODE_TO_FULL = {
    'Nak': 'Nakamura, Hikaru', 'Car': 'Caruana, Fabiano',
    'Gir': 'Giri, Anish', 'Pra': 'Praggnanandhaa R',
    'Wei': 'Wei, Yi', 'Sin': 'Sindarov, Javokhir',
    'Esi': 'Esipenko, Andrey', 'Blu': 'Bluebaum, Matthias',
}

# For each sim, compute the winner's total score
# Each game col like "Sin|Esi" means Sin is white. Value 1.0 = white wins, 0.0 = black wins, 0.5 = draw
# Player's score = sum of results where they play white + sum of (1 - result) where they play black + current standing points

player_scores = {}
for code in PLAYERS:
    white_cols = [c for c in game_cols if c.split('|')[0] == code]
    black_cols = [c for c in game_cols if c.split('|')[1] == code]
    score = STANDINGS[code]
    for c in white_cols:
        score = score + df[c]
    for c in black_cols:
        score = score + (1.0 - df[c])
    player_scores[code] = score

# Get the winner's score for each simulation
winner_scores = []
for code, full_name in CODE_TO_FULL.items():
    mask = df['winner'] == full_name
    if mask.any():
        winner_scores.append(player_scores[code][mask])

all_winner_scores = pd.concat(winner_scores)
print(f"  Average winning score: {all_winner_scores.mean():.2f}")
print(f"  Median winning score: {all_winner_scores.median():.1f}")
print(f"  Min winning score: {all_winner_scores.min():.1f}")
print(f"  Max winning score: {all_winner_scores.max():.1f}")

# Distribution of winning scores
print(f"\n  Winning score distribution:")
score_counts = all_winner_scores.value_counts().sort_index()
for score, count in score_counts.items():
    pct = count / len(all_winner_scores) * 100
    print(f"    {score:5.1f}: {pct:5.1f}%")

# ============================================================
# 5. Most impactful remaining games
# ============================================================
print("\n" + "="*60)
print("5. MOST IMPACTFUL REMAINING GAMES")
print("="*60)

# Filter to games with meaningful variance (min 1% of sims in each outcome bucket)
min_count = int(n * 0.01)  # at least 1% of sims

impacts = []
for col in remaining_games:
    white_code, black_code = col.split('|')
    white_name = PLAYERS.get(white_code, white_code)
    black_name = PLAYERS.get(black_code, black_code)

    white_wins_mask = df[col] == 1.0
    black_wins_mask = df[col] == 0.0
    draw_mask = df[col] == 0.5

    n_ww = white_wins_mask.sum()
    n_bw = black_wins_mask.sum()
    n_draw = draw_mask.sum()

    # Skip games where one outcome is too rare (likely already played/fixed)
    if n_ww < min_count or n_bw < min_count:
        continue

    # For each player, compute win% swing
    max_swing = 0
    swing_details = {}
    for code, full_name in CODE_TO_FULL.items():
        win_pct_when_white_wins = (df.loc[white_wins_mask, 'winner'] == full_name).sum() / n_ww * 100
        win_pct_when_black_wins = (df.loc[black_wins_mask, 'winner'] == full_name).sum() / n_bw * 100
        swing = abs(win_pct_when_white_wins - win_pct_when_black_wins)
        swing_details[PLAYERS[code]] = (win_pct_when_white_wins, win_pct_when_black_wins, swing)
        if swing > max_swing:
            max_swing = swing

    impacts.append({
        'game': col,
        'white': white_name,
        'black': black_name,
        'max_swing': max_swing,
        'details': swing_details,
        'n_white_wins': n_ww,
        'n_black_wins': n_bw,
        'n_draws': n_draw,
    })

print(f"\n  Games with meaningful variance (>{min_count} sims each for W/B wins): {len(impacts)}")

impacts.sort(key=lambda x: x['max_swing'], reverse=True)

for i, imp in enumerate(impacts[:5]):
    print(f"\n  #{i+1}: {imp['white']} (W) vs {imp['black']} (B)  [column: {imp['game']}]")
    print(f"       Game outcomes in sims: White wins {imp['n_white_wins']:,}, Draw {imp['n_draws']:,}, Black wins {imp['n_black_wins']:,}")
    print(f"       Max win% swing: {imp['max_swing']:.1f} percentage points")
    print(f"       Player win% when White wins vs Black wins:")
    for player, (ww, bw, sw) in sorted(imp['details'].items(), key=lambda x: -x[1][2]):
        if sw > 0.5:  # Only show meaningful swings
            print(f"         {player:20s}: {ww:6.2f}% vs {bw:6.2f}% (swing: {sw:.1f}pp)")

print("\n" + "="*60)
print("DONE")
print("="*60)
