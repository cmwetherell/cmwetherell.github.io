---
layout: post
title:  "Building a Better Chess Complexity Model"
subtitle: "How we trained an ensemble model on 410,000 Stockfish-evaluated positions"
date:   2026-04-15 00:00:00 -0700
postImage: /assets/img/chess-complexity-ai.png
imageCaption: ""
categories: Analysis
---

Not every chess position is created equal. Some are dead draws where the best move is obvious. Others are double-edged middlegames where even grandmasters struggle.

**Elocator** is our tool for quantifying this — assigning a complexity score from 1 to 100 to any chess position, based on how much "win percentage" a player is likely to lose by making a move.

We recently overhauled the model behind Elocator, and the results are a meaningful step forward. Here's what we did, what we learned, and why it matters for chess analysis.

## What Does Complexity Look Like?

Before diving into the technical details, let's look at what the model actually sees. Here are four positions from real games at different complexity levels — click any board to explore the position on Lichess:

<div style="display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin: 30px 0;">
  <div style="text-align: center; flex: 1; min-width: 180px; max-width: 220px;">
    <a href="https://lichess.org/analysis/standard/8/8/4k3/8/8/3K4/4P3/8_w_-_-_0_1" target="_blank" rel="noopener">
      <img src="https://lichess1.org/export/fen.gif?fen=8/8/4k3/8/8/3K4/4P3/8+w+-+-+0+1&color=white&theme=brown&piece=cburnett" alt="Simple endgame - King and pawn vs King" style="width: 100%; border-radius: 4px;" />
    </a>
    <p style="margin-top: 8px;"><strong style="color: #10b981;">Score: 4/100</strong><br/><small>K+P vs K endgame. Only one idea — push the pawn.</small></p>
  </div>
  <div style="text-align: center; flex: 1; min-width: 180px; max-width: 220px;">
    <a href="https://lichess.org/analysis/standard/r1bq1rk1/ppppnppp/4p3/8/1bBP4/2N1PN2/PP3PPP/R1BQ1RK1_w_-_-_0_8" target="_blank" rel="noopener">
      <img src="https://lichess1.org/export/fen.gif?fen=r1bq1rk1/ppppnppp/4p3/8/1bBP4/2N1PN2/PP3PPP/R1BQ1RK1+w+-+-+0+8&color=white&theme=brown&piece=cburnett" alt="Quiet Italian middlegame" style="width: 100%; border-radius: 4px;" />
    </a>
    <p style="margin-top: 8px;"><strong style="color: #86efac;">Score: 25/100</strong><br/><small>Quiet Italian middlegame. Several reasonable plans, but low stakes.</small></p>
  </div>
  <div style="text-align: center; flex: 1; min-width: 180px; max-width: 220px;">
    <a href="https://lichess.org/analysis/standard/r1b2rk1/2q1bppp/p2p1n2/np2p3/3PP3/2N1BN1P/PPBQ1PP1/R4RK1_w_-_-_0_13" target="_blank" rel="noopener">
      <img src="https://lichess1.org/export/fen.gif?fen=r1b2rk1/2q1bppp/p2p1n2/np2p3/3PP3/2N1BN1P/PPBQ1PP1/R4RK1+w+-+-+0+13&color=white&theme=brown&piece=cburnett" alt="Tense Ruy Lopez middlegame" style="width: 100%; border-radius: 4px;" />
    </a>
    <p style="margin-top: 8px;"><strong style="color: #f59e0b;">Score: 62/100</strong><br/><small>Tense Ruy Lopez. Multiple pawn breaks, piece sacrifices in the air.</small></p>
  </div>
  <div style="text-align: center; flex: 1; min-width: 180px; max-width: 220px;">
    <a href="https://lichess.org/analysis/standard/r1bq1r1k/1p2bppp/p1np4/4p2n/2B1P2N/1BNP2Q1/PPP2PPP/R3R1K1_w_-_-_0_14" target="_blank" rel="noopener">
      <img src="https://lichess1.org/export/fen.gif?fen=r1bq1r1k/1p2bppp/p1np4/4p2n/2B1P2N/1BNP2Q1/PPP2PPP/R3R1K1+w+-+-+0+14&color=white&theme=brown&piece=cburnett" alt="Chaotic tactical middlegame" style="width: 100%; border-radius: 4px;" />
    </a>
    <p style="margin-top: 8px;"><strong style="color: #ef4444;">Score: 95/100</strong><br/><small>Pieces swarming the kingside. Sacrificial ideas on f7, g6, multiple defensive tries.</small></p>
  </div>
</div>

A score of 50 means the position is more complex than half of all positions in our calibration dataset (35,739 classical OTB games between 2000+ rated players). A score of 100 means it's more complex than 99% of positions.

## The Problem

Given a chess position (represented as a FEN string), predict how "hard" it is — that is, how much win equity a typical strong player would lose by playing their move.

This matters because position complexity is the key ingredient for **estimating player strength from game data**. A 2800-rated player and a 1500-rated player will both find the right move in a simple position, but diverge sharply in complex ones.

## The Data Pipeline

### Filtering 4.87 Million Games

We started with the [Caissabase](https://caissabase.co.uk/) database — 4.87 million chess games spanning over a century of competitive play. We filtered this down to **2.46 million classical over-the-board games** where both players were rated 2000+, removing:

- Online/internet games (chess.com, chess24, Titled Tuesday, etc.)
- Rapid, blitz, and bullet time controls
- Games shorter than 10 full moves (walkovers, administrative results)
- Games with missing Elo ratings

### Sampling and Evaluating

Rather than evaluating every move in every game (which would take months), we sampled **one random move per game**. For each sampled position, we ran **Stockfish 18 at depth 20** with a 10-second time cap, evaluating both the position before and after the move.

The "accuracy" metric is the win-percentage loss: how much the player's winning chances decreased by making that specific move. A perfect move has accuracy 0. A blunder might have accuracy 20+.

We ran this on a **192-core EC2 spot instance** with 24 parallel Stockfish processes. After deduplication, we ended up with **357,000 unique positions** with high-quality depth-20 evaluations.

### How Deep Is Deep Enough?

How deep does Stockfish need to search for the evaluations to be reliable? We tested depths 2 through 18 on 100 positions:

| Depth | Spearman Correlation | Speedup vs D18 |
|-------|---------------------|----------------|
| 6 | 0.30 | 684x |
| 8 | 0.44 | 208x |
| **10** | **0.64** | **60x** |
| 12 | 0.66 | 25x |
| 14 | 0.71 | 9x |
| 18 | 1.00 | 1x |

Depth 10 hits the sweet spot for bulk data generation — 60x faster than depth 18 with reasonable correlation. But for our final training labels, we used depth 20 to maximize quality.

## The Models

We tested **12 different model architectures** across two families:

**CNN family** — A convolutional neural network that processes the chess board as an 8x8 image with 18 channels (12 piece types + side-to-move + castling rights + en passant). It uses residual blocks with squeeze-and-excitation attention — a technique borrowed from computer vision that lets the network focus on the most important piece configurations.

**MLP family** — A traditional multi-layer perceptron (fully connected network) that takes a 780-dimensional feature vector encoding the position. Despite being architecturally simpler, these models benefited from aggressive regularization (50% dropout) that prevented overfitting.

## Results

We evaluated all models on a held-out test set of 35,740 positions. The **ensemble of the CNN and MLP** — averaging their normalized predictions — emerged as the best approach:

| Model | Pearson | Spearman | Lift Ratio |
|-------|---------|----------|-----------|
| CNN (heavy dropout) | **0.136** | 0.109 | **2.91x** |
| **Ensemble (CNN + MLP)** | **0.134** | **0.124** | **2.76x** |
| Retrained MLP | 0.117 | 0.123 | 2.36x |
| Old production model | 0.068 | 0.005 | 1.93x |

The ensemble captures the best of both worlds: the CNN excels at separating the most extreme positions (highest lift ratio), while the MLP provides better fine-grained ranking in the middle. Together, they complement each other.

<figure style="margin: 30px 0;">
  <img src="/assets/img/elocator-v2/lift_charts.png" alt="Lift charts comparing model performance" style="width: 100%; max-width: 900px;" />
  <figcaption style="margin-top: 8px; font-size: 0.85em; color: #666;"><em>How well does each model rank positions by complexity? We sort all 35,740 holdout positions by the model's predicted score, split into 10 equal groups, and measure the actual average complexity in each group. A good model produces a clean staircase — the group it ranks as "most complex" should actually have the highest real-world complexity. The CNN and Ensemble show clear staircases; the old model is nearly flat.</em></figcaption>
</figure>

### Where the Models Disagree

One of the most interesting analyses was looking at where the CNN and MLP **disagree**. The MLP essentially can't distinguish complexity levels in the upper range — it predicts roughly the same value for everything. The CNN, with its spatial awareness of piece configurations, catches the subtleties that the MLP misses. But in the lower and middle ranges, the MLP's heavier regularization gives it an edge.

This is exactly why ensembling works — the models fail in different ways.

<figure style="margin: 30px 0;">
  <img src="/assets/img/elocator-v2/disagreement_chart.png" alt="Disagreement chart between CNN and MLP" style="width: 100%; max-width: 900px;" />
  <figcaption style="margin-top: 8px; font-size: 0.85em; color: #666;"><em>Positions sorted by CNN/MLP prediction ratio. The CNN (blue) stays close to actual values across all bins, while the MLP (red) systematically underpredicts positions the CNN flags as complex.</em></figcaption>
</figure>

## What Surprised Us

**1. The original MLP architecture was hard to beat.** Despite trying residual connections, wider layers, different activations, and varying dropout rates, the original pyramidal MLP with 50% dropout was the best single-model ranker. Heavy dropout is a powerful regularizer.

**2. Data quality mattered more than architecture.** Our biggest improvement came from fixing a bug in the data pipeline (the original filter was running on the wrong file, processing only 30% of available games) and generating higher-quality Stockfish evaluations. Architecture changes gave marginal gains by comparison.

**3. Loss function matters for CNNs but not MLPs.** The CNN was sensitive to the choice of Tweedie vs. MSE loss and Softplus vs. Sigmoid output. The MLP performed about the same regardless.

## Try It Yourself

The Elocator tool is live at [pawnalyze.com/elocator](https://pawnalyze.com/elocator). Paste any FEN string or PGN and get instant complexity scores.

<figure style="margin: 30px 0;">
  <img src="/assets/img/elocator-v2/screenshot_elocator_ui.png" alt="Elocator UI on Pawnalyze" style="width: 100%; max-width: 700px; border-radius: 8px; border: 1px solid #333;" />
  <figcaption style="margin-top: 8px; font-size: 0.85em; color: #666;"><em>The Elocator interface on Pawnalyze. Paste a FEN string and get an instant complexity score on the 1-100 scale.</em></figcaption>
</figure>

You can also analyze complete games by pasting PGN:

<figure style="margin: 30px 0;">
  <img src="/assets/img/elocator-v2/screenshot_game_analysis.png" alt="Game analysis with complexity chart" style="width: 100%; max-width: 700px; border-radius: 8px; border: 1px solid #333;" />
  <figcaption style="margin-top: 8px; font-size: 0.85em; color: #666;"><em>Game analysis view showing complexity over the course of a game, with per-move evaluation and complexity breakdown by color.</em></figcaption>
</figure>

## The Production Model

Under the hood, the API runs an **ensemble** of two models:

1. **CNN** (1.9M parameters) — processes the board spatially through 6 residual blocks with squeeze-and-excitation attention
2. **MLP** (12.3M parameters) — processes a hand-crafted 780-dimensional feature vector through 7 layers with 50% dropout

Both predictions are normalized and averaged, then mapped to a percentile-based 1-100 score calibrated against 35,739 positions from classical OTB games.

## What's Next

The complexity model is the foundation for our next project: **Elo estimation from game analysis**. If you know how complex each position was and how well the player handled it, you can estimate their playing strength without needing their rating history.

A 2800-rated player should consistently outperform the model's expectations in complex positions. A 1500-rated player should match expectations in simple positions but fall short in complex ones. The gap between actual and expected performance, weighted by complexity, gives us an Elo estimate.

Stay tuned.
