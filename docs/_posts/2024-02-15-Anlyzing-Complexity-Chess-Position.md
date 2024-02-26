---
layout: post
title:  "Analyzing The Complexity of a Chess Position"
subtitle: "How hard is it to find a good move?"
date:   2024-02-15 12:00:00 -0700
postImage: /assets/img/chess-complexity-ai.png
imageCaption:  "photo: Midjourney"
categories: interesting
---

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 

<style>
    .field td {padding: 3px 3px; }
    .field th {padding: 3px 3px; }
    .narrow {width: 65%; margin: auto;}
    .post-header{
        margin-bottom: 10px;
    }
    .post-title{
        margin-bottom: 10px;
    }
    .pad{
        padding: 5px;
    }
.postImage {
  display: block;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  font-size: 12px;
  max-height: 400px;
  padding-top: 0px;
}

.postImage img {
  height: auto;
  max-height: 400px;
}

.caption {
  display: block;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  font-size: 12px;
}
</style>

### What makes a position complex?

If you asked a Grandmaster what would they say? And is the position complex for humans, computers, or both? Do you know if a position is complex when you look at it?

Today, I am introducing an open-source tool that predicts the complexity of a chess position *for a human*. The tool is called [Elocator][elocator], and I hope you find it *interesting*.

### So how does it work?

I chose to define complexity as the expected change in Win % after a move is made. Imagine a position where white has a +1 advantage from Stockfish. That implies a 59% win rate for white. Assuming Stockfish is perfect, a human can only play a move that is as good or worse than Stockfish (i.e., white can not play a move that does increases the win rate for white). We know that after the next move is played, white will have a 59% or lower chance of winning.

Depending on the position a grandmaster may find the best move, or maybe it's a really difficult position to find the best move. Over a large enough dataset we can make correlations between the state of the board and how much we expect the win % to go down after a move is made. As an example, over 20,000 moves, my data shows that a GM is expected to lose 1.4% win rate after a move is made in a position with a queen on the board, compared to 1.3% if there is no queen. That seems small, but also implies positions are about 7% more complex when there is a queen on the board (1.4/1.3).

I created a dataset of FENs mapped to the loss in Win % from a GM that made a move in that position (classical OTB games only). Underlying this tool is a neural network (AI, deep learning, yada yada) that has been trained on 100,000 chess moves made by grandmasters. The model has learned to predict the complexity of a position by learning the expected change in Win % after a move is made, as measured by Stockfish 16 at depth 20.

The model is then used to predict the complexity of a given position, 1-10. The model is not perfect, but it is a good starting point for understanding the complexity of a position. I look forward to making it better over time.

### How accurate is the complexity score?

When building a model like this it's good practice to use some of the data to build the model, and then set some data to the side. This let's us evaluate the model on data that wasn't used to build the model.

With roughly 100k moves in my dataset, I decided to keep 20,000 off to the side for evaluation, and I've plotted the model performance below.

**Actual vs. Predicted by Complexity Score**
<div>                        <script type="text/javascript">window.PlotlyConfig = {MathJaxConfig: 'local'};</script>
        <script type="text/javascript">/**
* plotly.js v2.27.0
* Copyright 2012-2023, Plotly, Inc.
* All rights reserved.
* Licensed under the MIT license
*/
/*! For license information please see plotly.min.js.LICENSE.txt */

You can see that the model is finding that the hardest 10% of moves in GM games are 6 times harder than the easiest moves! A GM is expected to have their win rate reduced by 3% in the most complex positions, compared to just 0.5% in the easiest positions.

### Model Limitations

There are many! I bet you can find some positions and say, "Why does the complexity score say it's hard? It was easy for me to find the best move".

The model is certainly not perfect. I'd claim it's a decent start. I have several ideas to make the model even better! I'd love some help pursuing that goal too. If you're interested please reach out. Two main things are creating a larger training dataset (e.g., using Lichess database instead of OTB games), and then creating a better structure for the neural network (e.g., mimic the Stockfish NN structure).

There's also other ways to think about the idea of "complexity". Some examples could be the likelihood of a GM making the top engine move given the position, or the difference between the "material imbalance" and the engine evaluation. Maybe "complexity" could be best approximated by a combination of these three and more ideas.

### Interesting: A Note on Cheating

Today's OTB cheating detection relies largely (though not entirely) on comparisons to engine evaluation over the course of a game. How often did a player pick the top engine move? How often was their move in the top 3 engine moves?

Imagine this: "Hey, Mr. GM we noticed you played the top engine move 30 moves straight, that's pretty unusual." GM responds, "Wow, that's impressive! I've been studying a lot, and tried to find a line with lot's of obvious moves for me to play. I guess it worked!"

Sometimes there will be "statistical anomalies" by pure chance alone. One in one million means that we expect it to happen, though rarely! Now if a player has many one in one million games in a row? That's odd. Or maybe they're just better than we thought they were. "Proof" is hard to find, aside from physical evidence.

Today's cheating algorithms are sophisticated enough for OTB play that suspicion can reasonably be raised without physical evidence. But, let's go back to the "defense" from the suspicious GM above. What if we could demonstrate that, the 30 positions encountered were indeed quite **complex**. And that, for a random stretch of 30 moves, the chance is one in one million. But, what if the complexity of those 30 positions is higher than average, and it's actually one in one billion, or trillion, that someone could perform this well? **Understanding the complexity of a chess position can inform us how difficult it is to find good engine moves over the board and fine-tune our suspicions of cheating.**

### What's Next?

I have a few short term goals:

1. Find a mechanism to turn the complexity score into game evaluations
2. Find a mechanism to turn a series of games into a tournament score.
3. Find a mechanism to identify outliers beyond some percentile (e.g., to identify cheating).

Longer term, I view this as an opportunity for the chess community to develop open source cheating detection, among other things.

You can learn more about the model and the dataset by visiting the [Elocator GitHub repository][gh].


[elocator]: https://www.chesselocator.com
[gh]: https://github.com/cmwetherell/elocator