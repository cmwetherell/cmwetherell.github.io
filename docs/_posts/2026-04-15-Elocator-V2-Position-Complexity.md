---
layout: post
title:  "Building a Better Chess Complexity Model"
subtitle: "How we trained an ensemble model on 410,000 Stockfish-evaluated positions"
date:   2026-04-15 00:00:00 -0700
postImage: /assets/img/chess-complexity-ai.png
imageCaption: ""
categories: Analysis
---

Not every chess position is created equal. Some are dead draws where the best move is obvious. Others are double-edged middlegames where even grandmasters struggle. **Elocator** is our tool for quantifying this — assigning a complexity score to any chess position based on how much "win percentage" a player is likely to lose by making a move.

We recently overhauled the model behind Elocator, and the results are a meaningful step forward. Here's what we did, what we learned, and why it matters for chess analysis.

## The Problem

Given a chess position (represented as a FEN string), predict how "hard" it is — that is, how much win equity a typical strong player would lose by playing their move. Easy positions (forced recaptures, obvious checks) should score low. Complex positions (dynamic sacrifices, long-term compensation, unclear pawn structures) should score high.

This matters because position complexity is the key ingredient for estimating player strength from game data. A 2800-rated player and a 1500-rated player will both find the right move in a simple position, but diverge sharply in complex ones.

## The Data Pipeline

### Step 1: Filtering 4.87 Million Games

We started with the [Caissabase](https://caissabase.co.uk/) database — 4.87 million chess games spanning over a century of competitive play. We filtered this down to **2.46 million classical over-the-board games** where both players were rated 2000+, removing:

- Online/internet games (chess.com, chess24, Titled Tuesday, etc.)
- Rapid, blitz, and bullet time controls
- Games shorter than 10 full moves (walkovers, administrative results)
- Games with missing Elo ratings

### Step 2: Sampling and Evaluating

Rather than evaluating every move in every game (which would take months), we sampled **one random move per game**. For each sampled position, we ran Stockfish 18 at depth 20 with a 10-second time cap, evaluating both the position before and after the move.

The "accuracy" metric is the win-percentage loss: how much the player's winning chances decreased by making that specific move. A perfect move has accuracy 0. A blunder might have accuracy 20+.

We ran this on a 192-core EC2 spot instance (c6a.48xlarge) with 24 parallel Stockfish processes, processing about 3 positions per second. After deduplication, we ended up with **357,000 unique positions** with high-quality depth-20 Stockfish evaluations.

### Step 3: Depth Sensitivity Analysis

How deep does Stockfish need to search for the evaluations to be reliable? We tested depths 2 through 18 on 100 positions and measured correlation with depth-18 as ground truth:

| Depth | Spearman | Speedup |
|-------|----------|---------|
| 6 | 0.30 | 684x |
| 8 | 0.44 | 208x |
| **10** | **0.64** | **60x** |
| 12 | 0.66 | 25x |
| 14 | 0.71 | 9x |
| 18 | 1.00 | 1x |

Depth 10 hits the sweet spot for data generation — 60x faster than depth 18 with 0.64 rank correlation. But for our final training labels, we used depth 20 with a 10-second time cap to maximize quality.

## The Models

We tested **12 different model architectures** across two families:

**CNN family** — SE-ResNet with spatial convolutions over an 8x8 board representation (18 input channels: 12 piece planes + side-to-move + castling + en passant):
- 128-channel / 6-block (~1.9M params), various dropout and loss configurations
- 64-channel / 4-block (~326K params)
- MSE loss with sigmoid output vs. Tweedie loss with Softplus output

**MLP family** — Fully-connected networks taking a 780-dimensional feature vector (flattened piece arrays + castling + en passant, mirrored for Black):
- Original pyramidal shape (4096 → 2056 → 512 → 128 → 64 → 8 → 1, 12.3M params)
- Wide shallow (2048 → 2048 → 512)
- Residual MLP with skip connections
- Deep narrow (512 → 512 → 512 → 512 → 256)

## Results

We evaluated all models on a held-out test set of 35,740 positions. The key metric for our use case is **Pearson correlation** — we need the model's predicted complexity to correlate with actual move difficulty, since we'll compare a player's actual performance against the model's expectations.

<img src="/assets/img/elocator-v2/lift_charts.png" alt="Lift charts comparing model performance" style="width: 100%; max-width: 900px;" />

The **ensemble of the CNN and MLP** — averaging their normalized predictions — emerged as the best approach:

| Model | Pearson | Spearman | Lift |
|-------|---------|----------|------|
| CNN (heavy dropout) | 0.136 | 0.109 | 2.91x |
| **Ensemble (CNN + MLP)** | **0.134** | **0.124** | **2.76x** |
| Retrained MLP | 0.117 | 0.123 | 2.36x |
| Old production model | 0.068 | 0.005 | 1.93x |

The ensemble captures the best of both worlds: the CNN excels at separating the most extreme positions (highest lift ratio), while the MLP provides better fine-grained ranking in the middle (highest Spearman). Together, they complement each other.

### Where Models Disagree

One of the most interesting analyses was looking at where the CNN and MLP **disagree**:

<img src="/assets/img/elocator-v2/disagreement_chart.png" alt="Disagreement chart between CNN and MLP" style="width: 100%; max-width: 900px;" />

When sorted by the ratio of CNN prediction to MLP prediction, the CNN (blue) stays close to the actual values across all bins, while the MLP (red) systematically underpredicts positions that the CNN flags as complex. The MLP essentially can't distinguish complexity levels in the upper range — it predicts roughly the same value for everything the CNN thinks is hard.

## What Surprised Us

1. **The original MLP architecture was hard to beat.** Despite trying residual connections, wider layers, different activations (SiLU), and varying dropout rates, the original pyramidal MLP with 50% dropout was the best single-model ranker. The heavy dropout acts as a powerful regularizer that prevents overfitting even with millions of parameters.

2. **CNN input encoding didn't help the MLP.** Flattening the CNN's 18x8x8 spatial tensor to feed into an MLP performed *worse* than the hand-crafted 780-dimensional encoding. The spatial redundancy in the raw tensor hurts when processed by linear layers.

3. **Loss function matters for CNNs but not MLPs.** The CNN was sensitive to the choice of Tweedie vs. MSE loss and Softplus vs. Sigmoid output. The MLP performed about the same regardless — its heavy dropout dominates the training dynamics.

4. **Data quality > data quantity > model architecture.** Our biggest improvement came from generating higher-quality training labels (depth 20 vs. the original depth 20 on a much smaller dataset filtered incorrectly). The second biggest came from having 3.4x more data. Architecture changes gave marginal gains.

## The New Production Model

The Elocator API now uses a **100-point complexity scale** powered by the ensemble model. For each position:

1. The CNN (1.9M params) processes an 18x8x8 spatial tensor through 6 residual blocks with squeeze-and-excitation attention
2. The MLP (12.3M params) processes a 780-dimensional feature vector through 7 fully-connected layers with 50% dropout
3. Both predictions are normalized and averaged
4. The result is mapped to a 1-100 complexity score calibrated against the validation set

Score 1 = a position where the best move is essentially forced. Score 100 = a position where even grandmasters are likely to lose significant winning chances.

## What's Next

The complexity model is the foundation for our next project: **Elo estimation from game analysis**. The idea is straightforward — if you know how complex each position was and how well the player handled it, you can estimate their playing strength without needing their rating history.

A 2800-rated player should consistently outperform the model's expectations in complex positions. A 1500-rated player should match expectations in simple positions but fall short in complex ones. The gap between actual performance and expected performance, weighted by position complexity, gives us an Elo estimate.

Stay tuned.
