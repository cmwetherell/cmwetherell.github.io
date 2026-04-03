"""
Generate chart: Score-to-Win Conversion Rate for 2026 Candidates.
2x4 subplot grid: one panel per player with score distribution histogram
and conversion rate line.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_URL = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DATABASE']}"
    f"?sslmode=require"
)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CODES = ['Nak', 'Car', 'Gir', 'Pra', 'Wei', 'Sin', 'Esi', 'Blu']

SHORT_NAMES = {
    'Nak': 'Nakamura',
    'Car': 'Caruana',
    'Gir': 'Giri',
    'Pra': 'Praggnanandhaa',
    'Wei': 'Wei Yi',
    'Sin': 'Sindarov',
    'Esi': 'Esipenko',
    'Blu': 'Bluebaum',
}

FULL_NAMES = {
    'Nak': 'Nakamura, Hikaru',
    'Car': 'Caruana, Fabiano',
    'Gir': 'Giri, Anish',
    'Pra': 'Praggnanandhaa R',
    'Wei': 'Wei, Yi',
    'Sin': 'Sindarov, Javokhir',
    'Esi': 'Esipenko, Andrey',
    'Blu': 'Bluebaum, Matthias',
}

PLAYER_COLORS = {
    'Sin': '#3498DB',
    'Car': '#E74C3C',
    'Gir': '#FFB703',
    'Pra': '#2ECC71',
    'Wei': '#9B59B6',
    'Nak': '#1B2838',
    'Esi': '#F39C12',
    'Blu': '#95A5A6',
}

# Player order by current win probability (descending)
PLAYER_ORDER = ['Sin', 'Car', 'Gir', 'Pra', 'Wei', 'Nak', 'Blu', 'Esi']

# --- Load data ---
print("Connecting to database...")
engine = create_engine(DB_URL)
df = pd.read_sql("SELECT * FROM candidates_2026", engine)
print(f"Loaded {len(df):,} simulations")

# --- Compute each player's total score per simulation ---
for code in CODES:
    white_cols = [f"{code}|{opp}" for opp in CODES if opp != code]
    black_cols = [f"{opp}|{code}" for opp in CODES if opp != code]
    white_score = df[white_cols].sum(axis=1)
    black_score = (1 - df[black_cols]).sum(axis=1)
    df[f"score_{code}"] = white_score + black_score

# --- Build conversion data ---
# Round scores to nearest 0.5
for code in CODES:
    df[f"score_{code}_r"] = (df[f"score_{code}"] * 2).round() / 2

# For each player and score, compute win rate
results = []
for code in CODES:
    score_col = f"score_{code}_r"
    grouped = df.groupby(score_col).agg(
        count=('winner', 'size'),
        wins=('winner', lambda x: (x == FULL_NAMES[code]).sum())
    ).reset_index()
    grouped.columns = ['score', 'count', 'wins']
    grouped['win_pct'] = grouped['wins'] / grouped['count'] * 100
    grouped['player'] = code
    results.append(grouped)

all_results = pd.concat(results, ignore_index=True)

# --- Print stats ---
print("\n" + "="*70)
print("SCORE AT WHICH EACH PLAYER CROSSES 50% WIN PROBABILITY")
print("="*70)
for code in CODES:
    player_data = all_results[(all_results['player'] == code) & (all_results['count'] >= 100)].sort_values('score')
    crossed = player_data[player_data['win_pct'] >= 50.0]
    if len(crossed) > 0:
        cross_score = crossed.iloc[0]['score']
        cross_pct = crossed.iloc[0]['win_pct']
        cross_n = int(crossed.iloc[0]['count'])
        print(f"  {SHORT_NAMES[code]:15s}: score {cross_score:.1f} -> {cross_pct:.1f}% win rate (n={cross_n:,})")
    else:
        print(f"  {SHORT_NAMES[code]:15s}: never crosses 50% (with n>=100)")

# --- Build 2x4 subplot chart ---
subplot_titles = [SHORT_NAMES[code] for code in PLAYER_ORDER]

fig = make_subplots(
    rows=2, cols=4,
    subplot_titles=subplot_titles,
    specs=[[{"secondary_y": True}]*4]*2,
    horizontal_spacing=0.06,
    vertical_spacing=0.15,
)

for idx, code in enumerate(PLAYER_ORDER):
    row = idx // 4 + 1
    col = idx % 4 + 1

    # --- Score distribution histogram (all sims) ---
    score_col = f"score_{code}_r"
    score_counts = df[score_col].value_counts().sort_index()

    # Scale histogram so tallest bar ~ 65% of chart height (win% goes 0-100)
    max_count = score_counts.max()
    scale_factor = 65.0 / max_count if max_count > 0 else 1

    fig.add_trace(
        go.Bar(
            x=score_counts.index,
            y=score_counts.values * scale_factor,
            marker=dict(
                color='rgba(180,180,180,0.4)',
                line=dict(width=0),
            ),
            width=0.45,
            showlegend=False,
            hoverinfo='skip',
        ),
        row=row, col=col,
        secondary_y=True,
    )

    # --- Conversion rate line ---
    player_data = all_results[
        (all_results['player'] == code) & (all_results['count'] >= 100)
    ].sort_values('score')

    if len(player_data) > 0:
        fig.add_trace(
            go.Scatter(
                x=player_data['score'],
                y=player_data['win_pct'],
                mode='lines+markers',
                line=dict(color=PLAYER_COLORS[code], width=2.5),
                marker=dict(size=5, color=PLAYER_COLORS[code]),
                showlegend=False,
                hovertemplate=(
                    f"<b>{SHORT_NAMES[code]}</b><br>"
                    "Score: %{x:.1f}<br>"
                    "Win rate: %{y:.1f}%<br>"
                    "Simulations: %{customdata:,}<extra></extra>"
                ),
                customdata=player_data['count'],
            ),
            row=row, col=col,
            secondary_y=False,
        )

# --- Style axes ---
for idx, code in enumerate(PLAYER_ORDER):
    row = idx // 4 + 1
    col = idx % 4 + 1

    # Primary y-axis (win %)
    fig.update_yaxes(
        range=[0, 100],
        gridcolor='#E8E8E8',
        gridwidth=1,
        zeroline=False,
        ticksuffix='%',
        showticklabels=(col == 1),
        title_text=("Win %" if col == 1 else None),
        secondary_y=False,
        row=row, col=col,
    )

    # Secondary y-axis (histogram) - hidden
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        secondary_y=True,
        row=row, col=col,
    )

    # X-axis
    fig.update_xaxes(
        range=[6.5, 12.5],
        dtick=1,
        gridcolor='#E8E8E8',
        gridwidth=1,
        zeroline=False,
        title_text=("Score" if row == 2 else None),
        row=row, col=col,
    )

fig.update_layout(
    title=dict(
        text="If a Player Scores X Points, How Often Do They Win?",
        font=dict(size=20),
        x=0.5,
        xanchor='center',
    ),
    font=dict(
        family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        size=12,
        color="#2C3E50",
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=500,
    margin=dict(l=60, r=30, t=80, b=70),
    annotations=list(fig.layout.annotations) + [
        dict(
            text="Gray bars show score distribution | Based on 320,000 Monte Carlo simulations | Pawnalyze.com",
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=11, color="#999999"),
            xanchor="center",
        )
    ],
)

# Disable Plotly's binary encoding (bdata/dtype) so the output HTML uses
# plain JSON arrays compatible with the CDN version of plotly.js.
import _plotly_utils.utils as _pu
_orig_to_typed_array_spec = _pu.to_typed_array_spec
_pu.to_typed_array_spec = lambda v: v  # no-op: skip binary encoding

# Save as HTML snippet (no full page, no plotly.js include)
html_snippet = fig.to_html(
    full_html=False,
    include_plotlyjs=False,
    config={'displayModeBar': False},
    div_id="chart-score-conversion",
)

# Restore original function
_pu.to_typed_array_spec = _orig_to_typed_array_spec

output_path = os.path.join(OUTPUT_DIR, "chart_score_conversion.html")
with open(output_path, 'w') as f:
    f.write(html_snippet)

print(f"\nChart saved to: {output_path}")
print(f"HTML snippet size: {len(html_snippet):,} bytes")
