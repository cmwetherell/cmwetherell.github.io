---
layout: post
title:  "Richard Rapport Favorite To Win Candidates"
subtitle: "If he wears his pink suit every day"
date:   2022-06-28 00:00:00 -0600
postImage: /assets/img/RapportPink.jpeg # https://www.flickr.com/photos/fide/51782665101/
imageCaption:  "photo: FIDE/Stev Bonhage"
categories: chess-simulations
---

<!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>  -->

<style>
    .field td {padding: 3px 3px; }
    .field th {padding: 3px 3px; }
    .narrow {width: 50%; margin: auto;}
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

### Rapport On Perfect Score Wearing Pink Suit

Rapport taught us all a great lesson the other day, fashion choices **do** impact chess performance. Just look at that drippy suit! In Round 8, Jan-Krzysztof Duda accidentally looked at his opponents attire, and suddenly, dazed and confused, he played **27...b4??!**. Rapport never looked back.

At Pawnalyze, our goal is to make the most accurate tournament predictions and we are always looking for new infromation to improve our game prediction model. As we have learned from Rapport, we must also consider the art in chess when making predictions. To the rational observer, it is obvious that Rapport is unstoppable in his pink suit because he has a perfect 1/1 score in Candidates games while wearing it.

Therefore, we decided to update our machine learning model to reflect that if he wears a pink suit, he is guaranteed to win. With our new model (we call it PinkML v2), we can predict the outcome of the Candidates if he wears his pink suit for the remaining five games.

**Incredibly, Rapport is now the odds-on favorite to win the event.**


**2022 Candidates Tournament Probabilities**
*Assuming Rapport wears pink suit*
{: .narrow .pad}

| Name           |  Win %|
|:---------------|:-----:|
| Rapport        |  64.6 |
| Nepomniachtchi |  34.1 |
| Caruana        |   1.2 |
| Firouzja       |   0.0 |
| Nakamura       |   0.0 |
| Ding Liren     |   0.0 |
| Radjabov       |   0.0 |
| Duda           |   0.0 |
{: .field .narrow}

<br>
Look, I'm not an expert in chess tournament strategy. But, I do hope we can get this news to Rapport so he is aware of the fortune that awaits him if he brings back the pink suit!


[ml]: https://pawnalyze.com/tournament/2022/02/27/Elo-Rating-Accuracy-Is-Machine-Learning-Better.html
[cand]: https://github.com/cmwetherell/cmwetherell.github.io/blob/main/chessSim/candidatesTorunament.py
[git]: https://github.com/cmwetherell/cmwetherell.github.io/blob/main/chessSim/