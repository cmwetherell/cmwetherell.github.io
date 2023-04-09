---
layout: post
title:  "The Battle for the Vacant Throne: 2023 FIDE World Chess Championship"
shortTitle: '2023 WCC'
date: 2023-04-08 17:00:00 -0700
postImage: /assets/img/ding-nepo.jpeg # https://www.flickr.com/photos/fide/51782665101/in/photolist-2mTRGfH-2mF3T2E-2mFPiS8-2mGLprG-2mFPiSP-2mGHx2B-2mFraoE-2mH8cTG-2mGWPqT-2mbnW9r-2mbMGAE-2mFFqui-2mFTz2N-2mUmAc9-2mGhtwZ-2mbC9n9-2mFRHrs-2mFDYtd-2mGjizs-2mHa4JP-2mbihND-2mHccpR-2mGKNVX-2mGrZgb-2mbKy8k-2mGp2pN-2mGQHfx-2mbNKm2-2mGoSmJ-2mGoSoC-2mFRfug-2mFRfqP-2mFUBEj-2mFVCsk-2mFSnPS-2mFVCmy-2mGrg6K-2mFJEpo-2mHbFrj-2mHbFoi-2mH9npq-2mHcFF6-2mFDgYa-2mHcbab-2mK1g2L-2mGWPuF-2mH18QK-2mGZ8oD-2mGWPwE-2mGWPM4
imageCaption:  "photo: Candidates 2022 | Chess.com"
---

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
  max-height: 300px;
  padding-top: 0px;
}

.postImage img {
  height: auto;
  max-height: 300px;
}

.caption {
  display: block;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  font-size: 12px;
}

.yt {
  display: block;
  margin: 0 auto;
}

.chessable-logo {
display: flex;
justify-content: center;
}
.sponsor {
  text-align: center;
}


</style>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 
<!-- 
### Battle for the vacant throne -->

The 2023 FIDE World Chess Championship is set to take place in the city of Astana, Kazakhstan, where Ian Nepomniachtchi and Ding Liren will vie for the coveted title of World Chess Champion. The winner will succeed Magnus Carlsen, who has held the prestigious title since 2013, marking a near-decade-long reign.

### Predictions and Probabilities

As the championship unfolds, I will provide a detailed graph with round-by-round predictions. For now, my pre-match predictions suggest that Nepomniachtchi holds a slight edge, with a 53% chance of winning. The probability of the match proceeding to tiebreaks stands at 17%.

#### The Method Behind the Predictions

To calculate these predictions, I primarily employed my [usual methodology][usual], but given the significance of this event, I went the extra mile. I developed a model specifically tailored to predicting outcomes in world championship matches. For those interested in the technical aspects, I fine-tuned my customary LightGBM model to better predict world championship games. The fine-tuning process revealed that such games are more likely to end in a draw.

**Individual Game Model Predictions**

When Nepomniachtchi plays white, he has a 24.1% chance of winning, a 60.4% chance of a draw, and a 15.5% chance of Ding Liren emerging victorious. Conversely, when Ding Liren plays white, he has a 21.5% chance of winning, a 62.8% chance of a draw, and a 15.7% chance of Nepomniachtchi winning.

#### Fine-Tuned Model Differences
The primary difference between the fine-tuned model and the standard model is the slightly elevated draw rate. For instance, when Nepo is white, the draw rate increases from 57.2% to 60.4% in the fine-tuned model. Nepo's win rate decreases from 25.9% to 24.1%, while Ding Liren's win rate drops from 16.8% to 15.5%.

To stay updated with the latest predictions and insights, follow me on [Twitter!][twit]


[wiki]: https://en.wikipedia.org/wiki/Candidates_Tournament_2022
[twit]: https://twitter.com/pawnalyze

[usual]:https://pawnalyze.com/chess-simulations/2022/06/20/How-Our-Chess-Tournament-Predictions-Work.html
