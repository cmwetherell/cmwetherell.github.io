---
layout: post
title:  "2022 Candidates Tournament"
shortTitle: 'Candidates'
date: 2022-07-03 12:00:00 -0700
postImage: /assets/img/fabi-nepo.jpg # https://www.flickr.com/photos/fide/51782665101/in/photolist-2mTRGfH-2mF3T2E-2mFPiS8-2mGLprG-2mFPiSP-2mGHx2B-2mFraoE-2mH8cTG-2mGWPqT-2mbnW9r-2mbMGAE-2mFFqui-2mFTz2N-2mUmAc9-2mGhtwZ-2mbC9n9-2mFRHrs-2mFDYtd-2mGjizs-2mHa4JP-2mbihND-2mHccpR-2mGKNVX-2mGrZgb-2mbKy8k-2mGp2pN-2mGQHfx-2mbNKm2-2mGoSmJ-2mGoSoC-2mFRfug-2mFRfqP-2mFUBEj-2mFVCsk-2mFSnPS-2mFVCmy-2mGrg6K-2mFJEpo-2mHbFrj-2mHbFoi-2mH9npq-2mHcFF6-2mFDgYa-2mHcbab-2mK1g2L-2mGWPuF-2mH18QK-2mGZ8oD-2mGWPwE-2mGWPM4
imageCaption:  "photo: FIDE/Stev Bonhage"
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

}
</style>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 

### Nepo wins Candidates, Hikaru jumps into sole second place

With a draw in round 13, Ian Nepomniachtchi secured victory in the second straight Candidates Tournament officially earning himself a seat in the 2023 world championship match. Given Magnus comments, there is an outside chance that second place could matter. 

Second place is really simple: if Ding Liren beats Nakamura in round 14, Ding Liren will finish in second place. If they draw or Nakamura wins, Nakamura finishes in second place. The FIDE tiebreaker procedures don't matter - Nakamura or Ding Liren will have a clear second-place score.

[My model][model] predicts that Ding Liren has a 30% chance of winning. Presumably, he'll throw caution to the wind and sacrifice some drawing chances in favor of slightly improving his winning chances, just in case Magnus is not full of baloney. So maybe it's more like 35%?

GM Anish Giri has been posting recaps of each days games, which you can see below for Round 11:

<div class="ttt">
  <iframe width="560" height="315" class="yt" src="https://www.youtube.com/embed/j4GarKScv6o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
<br>

**And, now, predictions!**

**Second Place Probabilities**
*After Round 13*
{: .narrow .pad}

| Name           |   Second %|   Score |   SB |
|:---------------|---------:|--------:|-----:|
| Nakamura       |    70.06 |    7.50 | 46.00 |
| Ding Liren     |    29.94 |    7.00 | 42.00 |
| Nepomniachtchi |     0.00 |    9.00 | 54.25 |
| Radjabov       |     0.00 |    6.50 | 43.00 |
| Caruana        |     0.00 |    6.50 | 42.75 |
| Rapport        |     0.00 |    5.50 | 35.25 |
| Duda           |     0.00 |    5.00 | 31.25 |
| Firouzja       |     0.00 |    5.00 | 30.50 |
{: .field .narrow}
<br>

**2022 Candidates Tournament Probabilities**
*After Round 13*
{: .narrow .pad}

| Name           |   Win %|   Score |   TPR |
|:---------------|:------:|:--------:|:------:|
| Nepomniachtchi | 100.00 |    9.00 |  2919 |
| Nakamura       |   0.00 |    7.50 |  2832 |
| Ding Liren     |   0.00 |    7.00 |  2800 |
| Radjabov       |   0.00 |    6.50 |  2775 |
| Caruana        |   0.00 |    6.50 |  2769 |
| Rapport        |   0.00 |    5.50 |  2714 |
| Duda           |   0.00 |    5.00 |  2685 |
| Firouzja       |   0.00 |    5.00 |  2677 |
{: .field .narrow}
<br>
<div>                            <div id="c7642adb-8e47-423f-8f13-1284a672d38e" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("c7642adb-8e47-423f-8f13-1284a672d38e")) {                    Plotly.newPlot(                        "c7642adb-8e47-423f-8f13-1284a672d38e",                        [{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Ding Liren","marker":{"color":"rgb(27,158,119)","pattern":{"shape":""}},"name":"Ding Liren","offsetgroup":"Ding Liren","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[19.3,8.2,8.0,7.1,5.3,4.8,3.0,1.0,0.7,1.5,4.5,3.9,0.08,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Caruana","marker":{"color":"rgb(217,95,2)","pattern":{"shape":""}},"name":"Caruana","offsetgroup":"Caruana","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[16.8,26.5,27.0,25.2,22.9,21.4,28.4,28.7,16.3,11.2,3.7,0.0,0.0,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Firouzja","marker":{"color":"rgb(117,112,179)","pattern":{"shape":""}},"name":"Firouzja","offsetgroup":"Firouzja","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[15.1,14.5,14.8,12.2,4.7,3.7,0.6,0.2,0.1,0.3,0.0,0.0,0.0,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Nepomniachtchi","marker":{"color":"rgb(231,41,138)","pattern":{"shape":""}},"name":"Nepomniachtchi","offsetgroup":"Nepomniachtchi","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[13.2,24.7,24.2,25.4,42.2,44.0,54.6,66.6,75.2,84.6,85.8,95.0,99.86,100.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Rapport","marker":{"color":"rgb(102,166,30)","pattern":{"shape":""}},"name":"Rapport","offsetgroup":"Rapport","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[11.4,10.6,9.6,11.0,8.6,9.8,6.5,0.8,1.7,0.4,0.0,0.0,0.0,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Nakamura","marker":{"color":"rgb(230,171,2)","pattern":{"shape":""}},"name":"Nakamura","offsetgroup":"Nakamura","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[11.3,4.8,8.1,10.7,9.9,9.1,5.1,2.3,5.9,1.7,6.0,1.0,0.06,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Duda","marker":{"color":"rgb(166,118,29)","pattern":{"shape":""}},"name":"Duda","offsetgroup":"Duda","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[8.1,6.7,6.2,7.0,5.1,6.1,1.2,0.4,0.1,0.0,0.0,0.0,0.0,0.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Radjabov","marker":{"color":"rgb(102,102,102)","pattern":{"shape":""}},"name":"Radjabov","offsetgroup":"Radjabov","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","Round 1","Round 2","Round 3","Round 4","Round 5","Round 6","Round 7","Round 8","Round 9","Round 10","Round 11","Round 12","Round 13"],"xaxis":"x","y":[4.9,4.0,2.1,1.4,1.3,1.2,0.6,0.1,0.0,0.2,0.0,0.0,0.0,0.0],"yaxis":"y","type":"bar"}],                        {"barmode":"relative","hovermode":"x unified","legend":{"title":{"text":"Name"},"tracegroupgap":0,"traceorder":"reversed"},"margin":{"t":60},"template":{"data":{"barpolar":[{"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"bar":[{"error_x":{"color":"rgb(36,36,36)"},"error_y":{"color":"rgb(36,36,36)"},"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"carpet":[{"aaxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"baxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"type":"carpet"}],"choropleth":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"choropleth"}],"contourcarpet":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"contourcarpet"}],"contour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"contour"}],"heatmapgl":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmapgl"}],"heatmap":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmap"}],"histogram2dcontour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2dcontour"}],"histogram2d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2d"}],"histogram":[{"marker":{"line":{"color":"white","width":0.6}},"type":"histogram"}],"mesh3d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"mesh3d"}],"parcoords":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"parcoords"}],"pie":[{"automargin":true,"type":"pie"}],"scatter3d":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter3d"}],"scattercarpet":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattercarpet"}],"scattergeo":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergeo"}],"scattergl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergl"}],"scattermapbox":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattermapbox"}],"scatterpolargl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolargl"}],"scatterpolar":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolar"}],"scatter":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter"}],"scatterternary":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterternary"}],"surface":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"surface"}],"table":[{"cells":{"fill":{"color":"rgb(237,237,237)"},"line":{"color":"white"}},"header":{"fill":{"color":"rgb(217,217,217)"},"line":{"color":"white"}},"type":"table"}]},"layout":{"annotationdefaults":{"arrowhead":0,"arrowwidth":1},"autotypenumbers":"strict","coloraxis":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"colorscale":{"diverging":[[0.0,"rgb(103,0,31)"],[0.1,"rgb(178,24,43)"],[0.2,"rgb(214,96,77)"],[0.3,"rgb(244,165,130)"],[0.4,"rgb(253,219,199)"],[0.5,"rgb(247,247,247)"],[0.6,"rgb(209,229,240)"],[0.7,"rgb(146,197,222)"],[0.8,"rgb(67,147,195)"],[0.9,"rgb(33,102,172)"],[1.0,"rgb(5,48,97)"]],"sequential":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"sequentialminus":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]]},"colorway":["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD","#8C564B","#E377C2","#7F7F7F","#BCBD22","#17BECF"],"font":{"color":"rgb(36,36,36)"},"geo":{"bgcolor":"white","lakecolor":"white","landcolor":"white","showlakes":true,"showland":true,"subunitcolor":"white"},"hoverlabel":{"align":"left"},"hovermode":"closest","mapbox":{"style":"light"},"paper_bgcolor":"white","plot_bgcolor":"white","polar":{"angularaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","radialaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"scene":{"xaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"zaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"}},"shapedefaults":{"fillcolor":"black","line":{"width":0},"opacity":0.3},"ternary":{"aaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"baxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","caxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"title":{"x":0.05},"xaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"}}},"title":{"text":"Probability of Winning by Round | Pawnalyze.com"},"xaxis":{"anchor":"y","domain":[0.0,1.0],"title":{"text":"Round"}},"yaxis":{"anchor":"x","domain":[0.0,1.0],"range":[0,100],"title":{"text":"Win %"}}},                        {"responsive": true}                    )                };                            </script>        </div>


<br>

**The Field**

| Name           |   Classic |   Rapid |   Blitz |
|:---------------|:---------:|:-------:|:-------:|
| Ding Liren     |      2806 |    2836 |    2788 |
| Firouzja       |      2793 |    2670 |    2791 |
| Caruana        |      2783 |    2766 |    2847 |
| Nepomniachtchi |      2766 |    2821 |    2740 |
| Rapport        |      2764 |    2802 |    2613 |
| Nakamura       |      2760 |    2837 |    2850 |
| Duda           |      2750 |    2808 |    2779 |
| Radjabov       |      2738 |    2747 |    2684 |
{: .field}

Why am I including Rapid and Blitz ratings in a **Classical** tournament that is being played to determine who will go on to fight for the **Classical** chess world championship? Because there is a **whopping 22% chance the event is decided in Rapid or Blitz tiebreaks!** Of note, Firouzja's Rapid rating is likely well below his skill level. If his true skill level is higher than his current rating, I'm understating his chances of winning by about 2% below.

 **I'll keep this page updated as the tournament progresses, be sure to check back after each round!** In the meantime, follow me on [Twitter][twit] and let me know what you'd like to see on this page!



[wiki]: https://en.wikipedia.org/wiki/Candidates_Tournament_2022
[twit]: https://twitter.com/pawnalyze
[regs]: https://handbook.fide.com/files/handbook/Regulations_for_the_FIDE_Candidates_Tournament_2022.pdf
[bullet]: https://twitter.com/pawnalyze/status/1542350916409405441?s=20&t=qSrsX6mLumfQwBMFhet1mQ
[model]: https://pawnalyze.com/tournament/2022/02/27/Elo-Rating-Accuracy-Is-Machine-Learning-Better.html