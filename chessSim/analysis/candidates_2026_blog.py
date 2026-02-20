"""
Analysis script for 2026 FIDE Candidates Tournament blog post.
Generates 7 interactive Plotly charts and key statistics.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# --- Config ---
DB_URL = "postgresql+psycopg2://default:REDACTED_PASSWORD@ep-quiet-frog-a4jh8h5m-pooler.us-east-1.aws.neon.tech:5432/verceldb"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PLAYERS = {
    'Nak': ('Nakamura, Hikaru', 2810),
    'Car': ('Caruana, Fabiano', 2795),
    'Gir': ('Giri, Anish', 2760),
    'Pra': ('Praggnanandhaa R', 2758),
    'Wei': ('Wei, Yi', 2754),
    'Sin': ('Sindarov, Javokhir', 2726),
    'Esi': ('Esipenko, Andrey', 2698),
    'Blu': ('Bluebaum, Matthias', 2684),
}

SHORT_NAMES = {
    'Nakamura, Hikaru': 'Nakamura',
    'Caruana, Fabiano': 'Caruana',
    'Giri, Anish': 'Giri',
    'Praggnanandhaa R': 'Praggnanandhaa',
    'Wei, Yi': 'Wei Yi',
    'Sindarov, Javokhir': 'Sindarov',
    'Esipenko, Andrey': 'Esipenko',
    'Bluebaum, Matthias': 'Bluebaum',
}

CODES = list(PLAYERS.keys())
NAME_TO_CODE = {v[0]: k for k, v in PLAYERS.items()}

# Color palette
COLORS = {
    'navy': '#1B2838',
    'gold': '#FFB703',
    'blue': '#4A90D9',
    'green': '#2ECC71',
    'red': '#E74C3C',
    'light': '#ECF0F1',
    'text': '#2C3E50',
    'grid': '#E8E8E8',
    'orange': '#F39C12',
    'purple': '#9B59B6',
    'teal': '#1ABC9C',
}

PLAYER_COLORS = [
    '#1B2838',  # Nakamura - deep navy
    '#E74C3C',  # Caruana - red
    '#FFB703',  # Giri - gold
    '#2ECC71',  # Pragg - green
    '#9B59B6',  # Wei Yi - purple
    '#3498DB',  # Sindarov - blue
    '#F39C12',  # Esipenko - orange
    '#95A5A6',  # Bluebaum - gray
]

COMMON_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=14, color="#2C3E50"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=10, r=30, t=70, b=90),
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter, sans-serif", bordercolor="#ccc"),
)


def save_chart(fig, name):
    html = fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False})
    path = os.path.join(OUTPUT_DIR, f"{name}.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"  Saved: {path}")
    return html


def load_data(engine):
    print("Loading data from database...")
    df = pd.read_sql("SELECT * FROM candidates_2026", engine)
    print(f"  Loaded {len(df):,} simulations")
    return df


# ============================================================
# CHART 1: Win Probability Horizontal Bar
# ============================================================
def chart_win_probability(df):
    print("\nChart 1: Win Probability...")
    win_counts = df['winner'].value_counts()
    total = len(df)

    # Sort by win count descending
    names_sorted = [SHORT_NAMES[n] for n in win_counts.index]
    pcts = [(c / total) * 100 for c in win_counts.values]
    elos = [PLAYERS[NAME_TO_CODE[n]][1] for n in win_counts.index]

    # Reverse for horizontal bar (top player at top)
    names_sorted = names_sorted[::-1]
    pcts = pcts[::-1]
    elos = elos[::-1]

    # Color gradient from light gray (low) to deep navy (high)
    n = len(pcts)
    colors = [f'rgba(27, 40, 56, {0.3 + 0.7 * (i / (n - 1))})' for i in range(n)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names_sorted,
        x=pcts,
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=[f'{p:.1f}%' for p in pcts],
        textposition='outside',
        textfont=dict(size=14, color='#2C3E50', family="Inter, sans-serif"),
        hovertemplate='<b>%{y}</b><br>Win: %{x:.1f}%<br>Elo: %{customdata}<extra></extra>',
        customdata=elos,
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title=dict(text='Pre-Tournament Win Probability', font=dict(size=20), x=0.01),
        xaxis=dict(
            title='Win Probability (%)', showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, range=[0, max(pcts) * 1.2],
            ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14)),
        height=420,
        annotations=[dict(
            text='Based on 100,000 Monte Carlo simulations | Pawnalyze.com',
            xref='paper', yref='paper', x=1, y=-0.25,
            showarrow=False, font=dict(size=11, color='#999'),
            xanchor='right',
        )],
    )

    save_chart(fig, 'chart1_win_probability')

    # Print stats
    for name, pct, elo in zip(names_sorted[::-1], pcts[::-1], elos[::-1]):
        print(f"  {name} ({elo}): {pct:.1f}%")

    return fig


# ============================================================
# CHART 2: Win + 2nd Place Stacked Bar
# ============================================================
def chart_win_plus_second(df):
    print("\nChart 2: Win + 2nd Place...")
    total = len(df)

    win_counts = df['winner'].value_counts()
    second_counts = df['second'].value_counts()

    # Use same order as win probability (descending by win%)
    order = list(win_counts.index)

    data = []
    for name in order:
        short = SHORT_NAMES[name]
        win_pct = (win_counts.get(name, 0) / total) * 100
        second_pct = (second_counts.get(name, 0) / total) * 100
        data.append((short, win_pct, second_pct, win_pct + second_pct))

    # Reverse for horizontal bar
    data = data[::-1]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[d[0] for d in data],
        x=[d[1] for d in data],
        name='Win',
        orientation='h',
        marker=dict(color='#1B2838'),
        hovertemplate='<b>%{y}</b><br>Win: %{x:.1f}%<extra></extra>',
    ))

    fig.add_trace(go.Bar(
        y=[d[0] for d in data],
        x=[d[2] for d in data],
        name='2nd Place',
        orientation='h',
        marker=dict(color='#4A90D9'),
        hovertemplate='<b>%{y}</b><br>2nd Place: %{x:.1f}%<extra></extra>',
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        barmode='stack',
        title=dict(text='Win + Runner-Up Probability', font=dict(size=20), x=0.01),
        xaxis=dict(
            title='Probability (%)', showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=420,
        annotations=[
            dict(
                text='Based on 100,000 Monte Carlo simulations | Pawnalyze.com',
                xref='paper', yref='paper', x=1, y=-0.25,
                showarrow=False, font=dict(size=11, color='#999'),
                xanchor='right',
            )
        ] + [
            dict(
                text=f'{d[3]:.0f}%',
                x=d[3] + 0.8, y=d[0],
                showarrow=False, font=dict(size=12, color='#666'),
                xanchor='left',
            ) for d in data
        ],
    )

    save_chart(fig, 'chart2_win_plus_second')

    for d in reversed(data):
        print(f"  {d[0]}: Win {d[1]:.1f}% + 2nd {d[2]:.1f}% = {d[3]:.1f}%")

    return fig


# ============================================================
# CHART 3: Head-to-Head Expected Score Heatmap
# ============================================================
def chart_head_to_head(df):
    print("\nChart 3: Head-to-Head Heatmap...")

    short_labels = [SHORT_NAMES[PLAYERS[c][0]] for c in CODES]
    n = len(CODES)

    # Build matrices
    score_matrix = np.full((n, n), np.nan)
    win_matrix = np.full((n, n), np.nan)
    draw_matrix = np.full((n, n), np.nan)
    loss_matrix = np.full((n, n), np.nan)

    for i, wc in enumerate(CODES):
        for j, bc in enumerate(CODES):
            if wc == bc:
                continue
            col = f'{wc}|{bc}'
            if col in df.columns:
                vals = df[col]
                score_matrix[i][j] = vals.mean()
                win_matrix[i][j] = (vals == 1.0).mean() * 100
                draw_matrix[i][j] = (vals == 0.5).mean() * 100
                loss_matrix[i][j] = (vals == 0.0).mean() * 100

    # Custom hover text
    hover_text = []
    annotations_list = []
    for i in range(n):
        row_hover = []
        for j in range(n):
            if i == j:
                row_hover.append('')
            else:
                s = score_matrix[i][j]
                w = win_matrix[i][j]
                d = draw_matrix[i][j]
                l = loss_matrix[i][j]
                row_hover.append(
                    f'<b>{short_labels[i]}</b> (White) vs <b>{short_labels[j]}</b> (Black)<br>'
                    f'Expected Score: {s:.3f}<br>'
                    f'White Win: {w:.1f}% | Draw: {d:.1f}% | Black Win: {l:.1f}%'
                )
            # Text annotation
            if i != j:
                annotations_list.append(dict(
                    x=j, y=i,
                    text=f'{score_matrix[i][j]:.2f}',
                    showarrow=False,
                    font=dict(size=12, color='white' if abs(score_matrix[i][j] - 0.5) > 0.06 else '#333'),
                ))
        hover_text.append(row_hover)

    fig = go.Figure(data=go.Heatmap(
        z=score_matrix.tolist(),
        x=short_labels,
        y=short_labels,
        colorscale=[
            [0.0, '#C0392B'],    # strong black advantage
            [0.35, '#E74C3C'],   # moderate black advantage
            [0.47, '#FADBD8'],   # slight black advantage
            [0.5, '#FDFEFE'],    # even
            [0.53, '#D5F5E3'],   # slight white advantage
            [0.65, '#2ECC71'],   # moderate white advantage
            [1.0, '#1E8449'],    # strong white advantage
        ],
        zmin=0.35,
        zmax=0.65,
        hovertext=hover_text,
        hovertemplate='%{hovertext}<extra></extra>',
        colorbar=dict(
            title=dict(text='Expected<br>Score', side='right'),
            tickvals=[0.35, 0.425, 0.5, 0.575, 0.65],
            ticktext=['0.35', '0.425', '0.50', '0.575', '0.65'],
            len=0.8,
        ),
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title=dict(text='Head-to-Head Expected Score (White\'s Perspective)', font=dict(size=18), x=0.01),
        xaxis=dict(title='Black Player', side='bottom', tickfont=dict(size=13)),
        yaxis=dict(title='White Player', tickfont=dict(size=13), autorange='reversed'),
        height=520,
        width=620,
        annotations=annotations_list + [dict(
            text='Score > 0.50 = advantage for White | Pawnalyze.com',
            xref='paper', yref='paper', x=0.5, y=-0.25,
            showarrow=False, font=dict(size=11, color='#999'),
            xanchor='center',
        )],
    )

    save_chart(fig, 'chart3_head_to_head')

    # Print some highlights
    for i, wc in enumerate(CODES):
        for j, bc in enumerate(CODES):
            if wc != bc and score_matrix[i][j] is not np.nan:
                if score_matrix[i][j] > 0.58 or score_matrix[i][j] < 0.42:
                    print(f"  {short_labels[i]} vs {short_labels[j]}: {score_matrix[i][j]:.3f}")

    return fig


# ============================================================
# CHART 4: Tiebreak Impact (Dumbbell Chart)
# ============================================================
def chart_tiebreak_impact(df):
    print("\nChart 4: Tiebreak Impact...")

    total = len(df)
    tb_df = df[df['tie'] == 1]
    no_tb_df = df[df['tie'] == 0]

    tb_total = len(tb_df)
    no_tb_total = len(no_tb_df)

    print(f"  Tiebreak sims: {tb_total:,} ({100*tb_total/total:.1f}%)")
    print(f"  No tiebreak sims: {no_tb_total:,} ({100*no_tb_total/total:.1f}%)")

    tb_wins = tb_df['winner'].value_counts()
    no_tb_wins = no_tb_df['winner'].value_counts()

    data = []
    for name in df['winner'].value_counts().index:
        short = SHORT_NAMES[name]
        tb_pct = (tb_wins.get(name, 0) / tb_total) * 100
        no_tb_pct = (no_tb_wins.get(name, 0) / no_tb_total) * 100
        delta = tb_pct - no_tb_pct
        data.append((short, name, no_tb_pct, tb_pct, delta))

    # Sort by overall win% (ascending, so top player ends up at top of horizontal bar)
    overall_win = df['winner'].value_counts()
    total_sims = len(df)
    data.sort(key=lambda x: overall_win.get(x[1], 0) / total_sims)

    fig = go.Figure()

    # Lines connecting the dots
    for d in data:
        fig.add_trace(go.Scatter(
            x=[d[2], d[3]],
            y=[d[0], d[0]],
            mode='lines',
            line=dict(color='#BDC3C7', width=2),
            showlegend=False,
            hoverinfo='skip',
        ))

    # Classical (no tiebreak) dots
    fig.add_trace(go.Scatter(
        x=[d[2] for d in data],
        y=[d[0] for d in data],
        mode='markers',
        marker=dict(size=12, color='#1B2838', line=dict(width=1, color='white')),
        name='Classical Only',
        hovertemplate='<b>%{y}</b><br>Classical Only: %{x:.1f}%<extra></extra>',
    ))

    # Tiebreak dots
    fig.add_trace(go.Scatter(
        x=[d[3] for d in data],
        y=[d[0] for d in data],
        mode='markers',
        marker=dict(size=12, color='#FFB703', symbol='diamond', line=dict(width=1, color='white')),
        name='Tiebreak',
        hovertemplate='<b>%{y}</b><br>With Tiebreak: %{x:.1f}%<extra></extra>',
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title=dict(text='Win % by Tournament Outcome: Classical vs. Tiebreak', font=dict(size=18), x=0.01),
        xaxis=dict(
            title='Win Probability (%)', showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=420,
        annotations=[
            dict(
                text=f'Tiebreaks occur in {100*tb_total/total:.0f}% of simulations | Pawnalyze.com',
                xref='paper', yref='paper', x=1, y=-0.25,
                showarrow=False, font=dict(size=11, color='#999'),
                xanchor='right',
            )
        ] + [
            dict(
                text=f'{"+" if d[4] > 0 else ""}{d[4]:.1f}',
                x=max(d[2], d[3]) + 0.8, y=d[0],
                showarrow=False,
                font=dict(size=11, color='#2ECC71' if d[4] > 0 else '#E74C3C'),
                xanchor='left',
            ) for d in data
        ],
    )

    save_chart(fig, 'chart4_tiebreak_impact')

    for d in sorted(data, key=lambda x: -x[4]):
        print(f"  {d[0]}: Classical {d[2]:.1f}% → Tiebreak {d[3]:.1f}% (Δ {d[4]:+.1f})")

    return fig


# ============================================================
# CHART 5: Winning Score Distribution
# ============================================================
def chart_winning_score(df):
    print("\nChart 5: Winning Score Distribution...")

    # Compute winner's score for each simulation
    scores = []
    for _, row in df.iterrows():
        winner = row['winner']
        code = NAME_TO_CODE[winner]

        # Games as white: score is the column value
        white_games = [f'{code}|{opp}' for opp in CODES if opp != code]
        # Games as black: score is 1 - column value
        black_games = [f'{opp}|{code}' for opp in CODES if opp != code]

        score = sum(row[g] for g in white_games) + sum(1 - row[g] for g in black_games)
        scores.append(score)

    df_scores = pd.DataFrame({'winner': df['winner'], 'score': scores})

    print(f"  Mean winning score: {np.mean(scores):.2f}")
    print(f"  Median winning score: {np.median(scores):.2f}")
    print(f"  Min: {np.min(scores):.1f}, Max: {np.max(scores):.1f}")

    # Scores are discrete at 0.5 intervals -- count directly instead of binning
    score_values = sorted(set(np.arange(6.0, 14.5, 0.5)))  # all possible half-point scores
    bin_centers = [float(s) for s in score_values]

    # Compute per-player counts
    player_order = [PLAYERS[c][0] for c in CODES]  # full names in standard order
    player_short = [SHORT_NAMES[n] for n in player_order]

    score_series = pd.Series(scores)
    all_counts = [int((score_series == s).sum()) for s in bin_centers]

    player_counts = {}
    player_stats = {}
    for full_name, short_name in zip(player_order, player_short):
        p_scores = df_scores[df_scores['winner'] == full_name]['score'].values
        if len(p_scores) > 0:
            p_series = pd.Series(p_scores)
            player_counts[short_name] = [int((p_series == s).sum()) for s in bin_centers]
            player_stats[short_name] = (np.mean(p_scores), np.median(p_scores), len(p_scores))
        else:
            player_counts[short_name] = [0] * len(bin_centers)
            player_stats[short_name] = (0, 0, 0)

    mean_all, med_all = np.mean(scores), np.median(scores)

    # Build 2x4 subplot grid -- one histogram per player
    fig = make_subplots(
        rows=2, cols=4,
        subplot_titles=[f"{sn} ({player_stats[sn][2]:,} wins)" for sn in player_short],
        horizontal_spacing=0.06,
        vertical_spacing=0.15,
    )

    for i, (short_name, color) in enumerate(zip(player_short, PLAYER_COLORS)):
        row = i // 4 + 1
        col = i % 4 + 1
        mean_p, med_p, n_p = player_stats[short_name]

        fig.add_trace(go.Bar(
            x=bin_centers,
            y=player_counts[short_name],
            width=0.45,
            marker=dict(color=color, line=dict(color='white', width=0.5)),
            hovertemplate=f'<b>{short_name}</b><br>Score: %{{x:.1f}}<br>Count: %{{y:,}}<extra></extra>',
            showlegend=False,
        ), row=row, col=col)

        # Add mean line annotation
        if n_p > 0:
            fig.add_vline(
                x=mean_p, line=dict(color='#333', width=1.5, dash='dash'),
                row=row, col=col,
            )

    # Style all subplots
    fig.update_xaxes(showgrid=False, zeroline=False, dtick=1, tickfont=dict(size=10),
                     range=[7, 13])
    fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))

    # Add x-axis title only to bottom row
    for col in range(1, 5):
        fig.update_xaxes(title_text='Score', row=2, col=col, title_font=dict(size=11))

    fig.update_layout(
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12, color="#2C3E50"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=20, t=80, b=80),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, sans-serif", bordercolor="#ccc"),
        title=dict(text='What Score Does It Take to Win?', font=dict(size=20), x=0.01),
        height=500,
        annotations=list(fig.layout.annotations) + [
            dict(
                text=f'Overall average winning score: {mean_all:.1f} | Dashed line = player average | Pawnalyze.com',
                xref='paper', yref='paper', x=1, y=-0.15,
                showarrow=False, font=dict(size=11, color='#999'),
                xanchor='right',
            ),
        ],
    )

    save_chart(fig, 'chart5_winning_score')

    # Print score distribution
    for s in np.arange(6.0, 12.5, 0.5):
        count = sum(1 for sc in scores if s <= sc < s + 0.5)
        print(f"  Score {s:.1f}: {count:,} ({100*count/len(scores):.1f}%)")

    return fig


# ============================================================
# CHART 5b: Win Probability by Score (per player)
# ============================================================
def chart_win_pct_by_score(df):
    print("\nChart 5b: Win Probability by Score (faceted)...")

    player_order = [PLAYERS[c][0] for c in CODES]
    player_short = [SHORT_NAMES[n] for n in player_order]

    # Compute every player's score in every simulation
    player_scores = {}
    for code, (name, elo) in PLAYERS.items():
        short = SHORT_NAMES[name]
        white_cols = [f'{code}|{opp}' for opp in CODES if opp != code]
        black_cols = [f'{opp}|{code}' for opp in CODES if opp != code]
        score = sum(df[c] for c in white_cols) + sum(1 - df[c] for c in black_cols)
        player_scores[short] = score

    score_values = np.arange(7.0, 13.5, 0.5)

    fig = make_subplots(
        rows=2, cols=4,
        horizontal_spacing=0.065,
        vertical_spacing=0.15,
    )

    annotations = []

    for idx, (short_name, color) in enumerate(zip(player_short, PLAYER_COLORS)):
        row = idx // 4 + 1
        col = idx % 4 + 1

        scores = player_scores[short_name]
        is_winner = df['winner'] == [n for n in player_order if SHORT_NAMES[n] == short_name][0]

        x_vals = []
        y_vals = []
        hover_texts = []

        for s in score_values:
            mask = (scores >= s - 0.01) & (scores <= s + 0.01)
            n_at_score = mask.sum()
            if n_at_score >= 20:
                wins_at_score = (is_winner & mask).sum()
                win_pct = 100 * wins_at_score / n_at_score
                x_vals.append(float(s))
                y_vals.append(round(float(win_pct), 1))
                hover_texts.append(
                    f'<b>{short_name}</b> scores {s:.1f}<br>'
                    f'Win probability: {win_pct:.1f}%<br>'
                    f'({wins_at_score:,} wins out of {n_at_score:,} sims)'
                )

        if x_vals:
            print(f"  {short_name}: {len(x_vals)} score points, "
                  f"win% range {min(y_vals):.0f}%-{max(y_vals):.0f}%")

        # Area fill + line
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines+markers',
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)',
            showlegend=False,
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_texts,
        ), row=row, col=col)

        # Subplot title annotation
        axis_name = f'xaxis{idx+1}' if idx > 0 else 'xaxis'
        domain = fig.layout[axis_name]['domain']
        x_center = (domain[0] + domain[1]) / 2

        annotations.append(dict(
            text=f'<b>{short_name}</b>',
            font=dict(size=14),
            xref='paper', yref='paper',
            x=x_center, y=1.0 if row == 1 else 0.425,
            xanchor='center', yanchor='bottom',
            showarrow=False,
        ))

    # Update all axes
    for i in range(1, 9):
        xaxis = f'xaxis{i}' if i > 1 else 'xaxis'
        yaxis = f'yaxis{i}' if i > 1 else 'yaxis'
        fig.layout[xaxis].update(
            tickfont=dict(size=10), showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, dtick=1, range=[7, 13],
        )
        fig.layout[yaxis].update(
            tickfont=dict(size=10), showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, ticksuffix='%', range=[0, 105],
        )
        # Add "Score" label to bottom row
        if i >= 5:
            fig.layout[xaxis].update(title=dict(text='Score', font=dict(size=11)))

    annotations.append(dict(
        text='Minimum 20 simulations per point | Pawnalyze.com',
        xref='paper', yref='paper', x=1, y=-0.15,
        showarrow=False, font=dict(size=11, color='#999'),
        xanchor='right',
    ))

    fig.update_layout(
        font=dict(family='Inter, -apple-system, BlinkMacSystemFont, sans-serif', size=12, color='#2C3E50'),
        margin=dict(l=40, r=20, t=80, b=80),
        hoverlabel=dict(font=dict(size=12, family='Inter, sans-serif'), bgcolor='white', bordercolor='#ccc'),
        title=dict(text='If I Score X Points, How Often Do I Win?', font=dict(size=20), x=0.01),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=500,
        annotations=annotations,
    )

    save_chart(fig, 'chart5b_win_pct_by_score')
    return fig


# ============================================================
# CHART 6: Kingmaker Matchups (Most Impactful Games)
# ============================================================
def chart_kingmaker_matchups(df):
    print("\nChart 6: Kingmaker Matchups...")

    game_cols = [c for c in df.columns if '|' in c]
    total = len(df)

    # For each game, compute the max swing in any player's win%
    swings = []
    for col in game_cols:
        white_code, black_code = col.split('|')
        white_name = PLAYERS[white_code][0]
        black_name = PLAYERS[black_code][0]

        results = {}
        for result_val, result_label in [(1.0, 'White wins'), (0.5, 'Draw'), (0.0, 'Black wins')]:
            subset = df[df[col] == result_val]
            if len(subset) == 0:
                continue
            win_pcts = {}
            for player_name in df['winner'].unique():
                win_pcts[player_name] = (subset['winner'] == player_name).sum() / len(subset) * 100
            results[result_label] = win_pcts

        if len(results) < 3:
            continue

        # Find max swing for any player
        max_swing = 0
        swing_player = ''
        for player_name in df['winner'].unique():
            pcts = [results[r].get(player_name, 0) for r in ['White wins', 'Draw', 'Black wins']]
            swing = max(pcts) - min(pcts)
            if swing > max_swing:
                max_swing = swing
                swing_player = player_name

        swings.append({
            'game': col,
            'white': SHORT_NAMES[white_name],
            'black': SHORT_NAMES[black_name],
            'swing': max_swing,
            'swing_player': SHORT_NAMES[swing_player],
            'results': results,
        })

    swings.sort(key=lambda x: -x['swing'])
    top = swings[:10]

    print("  Top 10 most impactful matchups:")
    for s in top:
        print(f"    {s['white']} vs {s['black']}: {s['swing']:.1f}pp swing for {s['swing_player']}")

    # Build grouped bar chart for top 10
    game_labels = [f"{s['white']} vs {s['black']}" for s in top]
    game_labels = game_labels[::-1]  # reverse for horizontal

    # For each top game, show the swing player's win% under 3 scenarios
    white_wins_pcts = []
    draw_pcts = []
    black_wins_pcts = []

    for s in reversed(top):
        sp = s['swing_player']
        sp_full = [k for k, v in SHORT_NAMES.items() if v == sp][0]
        white_wins_pcts.append(s['results']['White wins'].get(sp_full, 0))
        draw_pcts.append(s['results']['Draw'].get(sp_full, 0))
        black_wins_pcts.append(s['results']['Black wins'].get(sp_full, 0))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=game_labels,
        x=white_wins_pcts,
        name='If White wins',
        orientation='h',
        marker=dict(color='#1B2838'),
        hovertemplate='%{y}<br>If White wins: %{x:.1f}%<extra></extra>',
    ))

    fig.add_trace(go.Bar(
        y=game_labels,
        x=draw_pcts,
        name='If Draw',
        orientation='h',
        marker=dict(color='#BDC3C7'),
        hovertemplate='%{y}<br>If Draw: %{x:.1f}%<extra></extra>',
    ))

    fig.add_trace(go.Bar(
        y=game_labels,
        x=black_wins_pcts,
        name='If Black wins',
        orientation='h',
        marker=dict(color='#4A90D9'),
        hovertemplate='%{y}<br>If Black wins: %{x:.1f}%<extra></extra>',
    ))

    # Add annotations showing whose odds swing
    swing_annotations = []
    for i, s in enumerate(reversed(top)):
        swing_annotations.append(dict(
            text=f'({s["swing_player"]})',
            x=max(white_wins_pcts[i], draw_pcts[i], black_wins_pcts[i]) + 1.5,
            y=game_labels[i],
            showarrow=False, font=dict(size=10, color='#999'),
            xanchor='left',
        ))

    layout_kwargs = {**COMMON_LAYOUT}
    layout_kwargs['margin'] = dict(l=10, r=80, t=70, b=90)
    fig.update_layout(
        **layout_kwargs,
        barmode='group',
        title=dict(text='Most Impactful Matchups: Who Swings the Most?', font=dict(size=17), x=0.01),
        xaxis=dict(
            title='Win Probability of Most Affected Player (%)',
            showgrid=True, gridcolor='#E8E8E8', zeroline=False, ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500,
        annotations=swing_annotations + [dict(
            text='Shows the player whose odds shift the most | Pawnalyze.com',
            xref='paper', yref='paper', x=1, y=-0.25,
            showarrow=False, font=dict(size=11, color='#999'),
            xanchor='right',
        )],
    )

    save_chart(fig, 'chart6_kingmaker_matchups')
    return fig


# ============================================================
# CHART 7: The Bluebaum Factor
# ============================================================
def chart_bluebaum_factor(df):
    print("\nChart 7: The Bluebaum Factor...")

    total = len(df)
    non_blu = df[df['winner'] != 'Bluebaum, Matthias']
    non_blu_total = len(non_blu)

    # For each non-Bluebaum player: compute W/D/L rates AND conditional tournament
    # winning chances for each outcome vs Bluebaum
    data = []
    for code, (name, elo) in PLAYERS.items():
        if code == 'Blu':
            continue
        short = SHORT_NAMES[name]
        is_winner = df['winner'] == name

        # As white vs Blu
        w_col = f'{code}|Blu'
        w_win_mask = df[w_col] == 1.0
        w_draw_mask = df[w_col] == 0.5
        w_loss_mask = df[w_col] == 0.0
        w_score = df[w_col].mean()

        w_win = w_win_mask.mean() * 100
        w_draw = w_draw_mask.mean() * 100
        w_loss = w_loss_mask.mean() * 100

        # Tournament win% conditional on each outcome (as White vs Blu)
        w_win_tourney = (is_winner & w_win_mask).sum() / w_win_mask.sum() * 100 if w_win_mask.sum() > 0 else 0
        w_draw_tourney = (is_winner & w_draw_mask).sum() / w_draw_mask.sum() * 100 if w_draw_mask.sum() > 0 else 0
        w_loss_tourney = (is_winner & w_loss_mask).sum() / w_loss_mask.sum() * 100 if w_loss_mask.sum() > 0 else 0

        # As black vs Blu
        b_col = f'Blu|{code}'
        b_win_mask = df[b_col] == 0.0   # player wins when Blu scores 0
        b_draw_mask = df[b_col] == 0.5
        b_loss_mask = df[b_col] == 1.0   # player loses when Blu scores 1
        b_score = 1 - df[b_col].mean()

        b_win = b_win_mask.mean() * 100
        b_draw = b_draw_mask.mean() * 100
        b_loss = b_loss_mask.mean() * 100

        # Tournament win% conditional on each outcome (as Black vs Blu)
        b_win_tourney = (is_winner & b_win_mask).sum() / b_win_mask.sum() * 100 if b_win_mask.sum() > 0 else 0
        b_draw_tourney = (is_winner & b_draw_mask).sum() / b_draw_mask.sum() * 100 if b_draw_mask.sum() > 0 else 0
        b_loss_tourney = (is_winner & b_loss_mask).sum() / b_loss_mask.sum() * 100 if b_loss_mask.sum() > 0 else 0

        total_expected = w_score + b_score
        overall_tourney = is_winner.mean() * 100

        data.append({
            'name': short,
            'total_expected': total_expected,
            'overall_tourney': overall_tourney,
            'w_win': w_win, 'w_draw': w_draw, 'w_loss': w_loss,
            'w_win_t': w_win_tourney, 'w_draw_t': w_draw_tourney, 'w_loss_t': w_loss_tourney,
            'b_win': b_win, 'b_draw': b_draw, 'b_loss': b_loss,
            'b_win_t': b_win_tourney, 'b_draw_t': b_draw_tourney, 'b_loss_t': b_loss_tourney,
        })

    # Sort by total expected score descending
    data.sort(key=lambda x: -x['total_expected'])

    print("\n  Expected score vs Bluebaum (2 games):")
    for d in data:
        print(f"    {d['name']}: {d['total_expected']:.3f} / 2.000 (overall tourney win: {d['overall_tourney']:.1f}%)")
        print(f"      As White: W {d['w_win']:.1f}% D {d['w_draw']:.1f}% L {d['w_loss']:.1f}%")
        print(f"        Tourney win if: W={d['w_win_t']:.1f}% D={d['w_draw_t']:.1f}% L={d['w_loss_t']:.1f}%")
        print(f"      As Black: W {d['b_win']:.1f}% D {d['b_draw']:.1f}% L {d['b_loss']:.1f}%")
        print(f"        Tourney win if: W={d['b_win_t']:.1f}% D={d['b_draw_t']:.1f}% L={d['b_loss_t']:.1f}%")

    # Build grouped bar charts showing tournament win% conditional on Bluebaum result
    names = [d['name'] for d in data][::-1]  # reverse for bottom-to-top

    # --- Chart 7a: As White vs Bluebaum ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=names,
        x=[d['w_win_t'] for d in data][::-1],
        name='Beat Bluebaum',
        orientation='h',
        marker=dict(color='#1E8449'),
        hovertemplate='<b>%{y}</b> beats Bluebaum (White)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['w_win_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig.add_trace(go.Bar(
        y=names,
        x=[d['w_draw_t'] for d in data][::-1],
        name='Drew Bluebaum',
        orientation='h',
        marker=dict(color='#BDC3C7'),
        hovertemplate='<b>%{y}</b> draws Bluebaum (White)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['w_draw_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig.add_trace(go.Bar(
        y=names,
        x=[d['w_loss_t'] for d in data][::-1],
        name='Lost to Bluebaum',
        orientation='h',
        marker=dict(color='#E74C3C'),
        hovertemplate='<b>%{y}</b> loses to Bluebaum (White)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['w_loss_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        barmode='group',
        title=dict(text='Tournament Win % by Result vs. Bluebaum (as White)', font=dict(size=17), x=0.01),
        xaxis=dict(
            title='Tournament Win Probability (%)', showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=420,
        annotations=[dict(
            text='How much does beating, drawing, or losing to Bluebaum affect your chances? | Pawnalyze.com',
            xref='paper', yref='paper', x=1, y=-0.25,
            showarrow=False, font=dict(size=11, color='#999'),
            xanchor='right',
        )],
    )

    save_chart(fig, 'chart7a_bluebaum_white')

    # --- Chart 7b: As Black vs Bluebaum ---
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        y=names,
        x=[d['b_win_t'] for d in data][::-1],
        name='Beat Bluebaum',
        orientation='h',
        marker=dict(color='#1E8449'),
        hovertemplate='<b>%{y}</b> beats Bluebaum (Black)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['b_win_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig2.add_trace(go.Bar(
        y=names,
        x=[d['b_draw_t'] for d in data][::-1],
        name='Drew Bluebaum',
        orientation='h',
        marker=dict(color='#BDC3C7'),
        hovertemplate='<b>%{y}</b> draws Bluebaum (Black)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['b_draw_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig2.add_trace(go.Bar(
        y=names,
        x=[d['b_loss_t'] for d in data][::-1],
        name='Lost to Bluebaum',
        orientation='h',
        marker=dict(color='#E74C3C'),
        hovertemplate='<b>%{y}</b> loses to Bluebaum (Black)<br>'
                      'Tournament win chance: %{x:.1f}%<br>'
                      '<extra></extra>',
        text=[f"{d['b_loss_t']:.0f}%" for d in data][::-1],
        textposition='outside',
        textfont=dict(size=11),
    ))

    fig2.update_layout(
        **COMMON_LAYOUT,
        barmode='group',
        title=dict(text='Tournament Win % by Result vs. Bluebaum (as Black)', font=dict(size=17), x=0.01),
        xaxis=dict(
            title='Tournament Win Probability (%)', showgrid=True, gridcolor='#E8E8E8',
            zeroline=False, ticksuffix='%',
        ),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=420,
        annotations=[dict(
            text='Even a draw against Bluebaum as Black keeps top players on track | Pawnalyze.com',
            xref='paper', yref='paper', x=1, y=-0.25,
            showarrow=False, font=dict(size=11, color='#999'),
            xanchor='right',
        )],
    )

    save_chart(fig2, 'chart7b_bluebaum_black')

    return fig, fig2


# ============================================================
# MAIN
# ============================================================
def main():
    engine = create_engine(DB_URL)
    df = load_data(engine)

    chart_win_probability(df)
    chart_win_plus_second(df)
    chart_head_to_head(df)
    chart_tiebreak_impact(df)
    chart_winning_score(df)
    chart_win_pct_by_score(df)
    chart_kingmaker_matchups(df)
    chart_bluebaum_factor(df)

    print("\n" + "=" * 60)
    print("All charts generated! HTML snippets saved to:", OUTPUT_DIR)
    print("=" * 60)


if __name__ == '__main__':
    main()
