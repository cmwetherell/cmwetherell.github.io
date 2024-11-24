---
layout: post
title:  "FIDE World Chess Championship 2024: Analysis and Predictions"
subtitle: "Can Ding return to form and defend his title against the Gukesh?"
date:   2024-11-24 00:00:00 -0700
postImage: /assets/img/ding_gukesh_opening.jpg
imageCaption:  "photo: Maria Emelianova"
categories: Tournament
---

<style>
  table {
        width: 70%;
    }
    table th, table td { padding: 5px 5px; }
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
  max-height: 315px;
  padding-top: 0px;
}

.postImage img {
  height: auto;
  max-height: 315px;
}

.caption {
  display: block;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  font-size: 12px;
}
</style>

### 2788 or 2675 Ding?

After defeating Ian Nepomniachtchi, Ding Liren held a rating of 2788. Since that time Ding Liren has scored only 20 points in 49 games, which gives a performance rating of a mere 2675 for the time period. Surely, he is capable of higher level chess than this. It remains to be seen which version of Ding Liren has arrived in Singapore. He shared in the Opening Ceremony that he feels relaxed, hass reviewed his recent games and hopes to bring back his "fighting spirit". I expect we'll see a version of Ding that reminds us of his 2023 performance - solid and exciting.

### Gukesh D: The new generation has arrived

Gukesh D won the Candidates in Toronto to give himself the opportunity of a lifetime, challenging a defending world champion that by all appearances is going to be a relatively easy opponent. Many pundits have Gukesh as the clear favorite. And Gukesh has been performing strongly including multiple months with a performance rating above 3000. In the same time period since the previous WCC, Gukesh has been much more active playing 172 games and notching 109.5 points for a TPR of 2762.

### Looking at the players performance
![Analyzing performance of Ding Liren and Gukesh D](/assets/img/wcc_tpr_24.png)

We can see that Gukesh has been far more active, and Ding Liren hasn't put together a 2700 level performance in all of 2024. How can we expect him to do it now? That's the intrigue of this match.

### My predictions

How should I decide what Elo to give Ding as an input to my predictions and simulations? I've taken various viewpoints over the last several weeks. First, I thought using his performance rating since the previous WCC would be most accurate - 2675. This would give him just a 10% chance to win the match. Using 2675 feels too punitive - he is clearly a stronger player than this. And the world championship is so important, he said he spent a few weeks perparing (more than last time!) and he is the defending champion, after all. So should we use his post match Elo of 2788 after he defeated Ian? That feels too generous.

I think his current Elo is actually a pretty good representation of what we can expect. Typically, I'd say that Elo is responding too slowly to performances that we've seen from him - but his experience and words suggest we'll see a stronger performance. So, in my simulations I'm going to use his current Elo. Ding Liren 2728 and Gukesh D 2783.

I simulated the tournament 10,000 times [(method)][method] and I've [published predictions][preds] in the simulations section of my website. I will update the predictions after each round with new simulations. You can also play prognosticator yourself and see how the predictions change based on the outcome of future rounds. Check it out!

![Pick the outcome of WCC games on Pawnalyze](/assets/img/gamepicker.png)

[sims]: https://www.pawnalyze.com/simulations/candidates-2024
[method]: https://blog.pawnalyze.com/chess-simulations/2022/06/20/How-Our-Chess-Tournament-Predictions-Work.html
[preds]: https://www.pawnalyze.com/simulations/fide-world-championship-singapore-2024