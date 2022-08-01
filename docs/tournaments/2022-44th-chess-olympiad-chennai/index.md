---
layout: post
title:  "44th Chess Olympiad Predictions"
shortTitle: 'Olympiad'
date: 2022-07-31 22:00:00 -0700
postImage: /assets/img/carlsenOlympiad.jpeg # https://www.flickr.com/photos/fide/51782665101/in/photolist-2mTRGfH-2mF3T2E-2mFPiS8-2mGLprG-2mFPiSP-2mGHx2B-2mFraoE-2mH8cTG-2mGWPqT-2mbnW9r-2mbMGAE-2mFFqui-2mFTz2N-2mUmAc9-2mGhtwZ-2mbC9n9-2mFRHrs-2mFDYtd-2mGjizs-2mHa4JP-2mbihND-2mHccpR-2mGKNVX-2mGrZgb-2mbKy8k-2mGp2pN-2mGQHfx-2mbNKm2-2mGoSmJ-2mGoSoC-2mFRfug-2mFRfqP-2mFUBEj-2mFVCsk-2mFSnPS-2mFVCmy-2mGrg6K-2mFJEpo-2mHbFrj-2mHbFoi-2mH9npq-2mHcFF6-2mFDgYa-2mHcbab-2mK1g2L-2mGWPuF-2mH18QK-2mGZ8oD-2mGWPwE-2mGWPM4
imageCaption:  "photo: FIDE / Lennart Ootes"
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



}
</style>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 

### US and India continue to win, Norway goes down in flames

As each round passes we see more and more close matchups and upsets. In Round 3, Norway was dealt a big blow by the Italian team and their 5.4% winning chances have plummeted to just 2.3%. In Round 4 the pairings are even more balanced so we should see many close matchups and many upsets. After Round 4, it will be difficult to call the outcome of any matchup an upset because all the piairings should be relatively balanced.

A key storyline so far in the event is the favorites to win entering the event, the United States, are currently back in 20th place in the standings. This is a little misleading, though, as they are still the favorites to win the event. The slow start will make it a bit harder to win in the tiebreaks (a version of Sonneborn-Berger), if it comes to that. But, their still likely to win the event outright, in which case it won't matter.

Apologies for not getting this page updated sooner. I was 'bug hunting' in my pairing algorithm and finally found a rogue '<' that was supposed to be '<='. 😱 It took more time and effort than I'd like to admit spending on finding it, but at least I can truthfully say I've learned some things about writing good code, unit testing, and debugging!

The format of this event creates a pretty slow start. If you look at how the win probabilities have changed after the first three rounds, it makes you wonder a little bit why we even play them! But, I don't think the goal is only to find the best team - there's benefits of a fun atmosphere where teams of all levels and players of all levels have a chance to compete, and then the event becomes more serious as it progresses.

I'll continue to update this page after every round so we can track how likely each country is to win. You may be familiar with my coverage of the [Candidates Tournament][cand] where I was running 10,000+ simulations. Because this tournament also requires a pairing algorithm to run after every round, each simulation takes more time and I'll probably stick between 1 and 5 thousand simulations in favor of getting the predictions out as soone as the games are over. I plan to make predictions available for each teams chances of medaling, and hope to do that soon!

<div class = 'sponsor' style="width:400px; margin:0 auto;">
These predictions brought to you by:
  <div class = 'chessable-logo' >
    <a href = 'https://chessable.com' >
    <img src='/assets/img/chessable.webp' width = '200' style= "margin:0 auto;">
    </a>
  </div>
</div>

<br>
**44th Chess Olympiad Predictions** <br>
*After Round 3*
<div>                            <div id="77001500-c55b-4295-aa4a-b987c3ad7a36" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("77001500-c55b-4295-aa4a-b987c3ad7a36")) {                    Plotly.newPlot(                        "77001500-c55b-4295-aa4a-b987c3ad7a36",                        [{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"United States of America","marker":{"color":"rgb(27,158,119)","pattern":{"shape":""}},"name":"United States of America","offsetgroup":"United States of America","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[62.2,60.7,63.4,62.7],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"India","marker":{"color":"rgb(217,95,2)","pattern":{"shape":""}},"name":"India","offsetgroup":"India","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[7.1,6.7,6.3,7.8],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Spain","marker":{"color":"rgb(117,112,179)","pattern":{"shape":""}},"name":"Spain","offsetgroup":"Spain","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[4.8,5.2,3.6,5.6],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Norway","marker":{"color":"rgb(231,41,138)","pattern":{"shape":""}},"name":"Norway","offsetgroup":"Norway","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[4.4,4.9,5.4,2.3],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Netherlands","marker":{"color":"rgb(102,166,30)","pattern":{"shape":""}},"name":"Netherlands","offsetgroup":"Netherlands","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[4.3,3.0,2.5,3.8],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Azerbaijan","marker":{"color":"rgb(230,171,2)","pattern":{"shape":""}},"name":"Azerbaijan","offsetgroup":"Azerbaijan","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[3.8,3.5,3.6,4.6],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertempla`te":"Win %{y}%","legendgroup":"Poland","marker":{"color":"rgb(166,118,29)","pattern":{"shape":""}},"name":"Poland","offsetgroup":"Poland","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[3.7,4.9,4.8,4.8],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"England","marker":{"color":"rgb(102,102,102)","pattern":{"shape":""}},"name":"England","offsetgroup":"England","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[2.4,2.1,2.2,1.5],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Ukraine","marker":{"color":"rgb(27,158,119)","pattern":{"shape":""}},"name":"Ukraine","offsetgroup":"Ukraine","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[2.0,2.8,2.0,2.0],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Germany","marker":{"color":"rgb(217,95,2)","pattern":{"shape":""}},"name":"Germany","offsetgroup":"Germany","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[1.8,2.2,2.3,0.9],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Armenia","marker":{"color":"rgb(117,112,179)","pattern":{"shape":""}},"name":"Armenia","offsetgroup":"Armenia","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.9,0.6,0.9,0.6],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"India 2","marker":{"color":"rgb(231,41,138)","pattern":{"shape":""}},"name":"India 2","offsetgroup":"India 2","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.7,1.2,0.9,1.5],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Iran","marker":{"color":"rgb(102,166,30)","pattern":{"shape":""}},"name":"Iran","offsetgroup":"Iran","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.6,0.4,0.9,0.5],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Croatia","marker":{"color":"rgb(230,171,2)","pattern":{"shape":""}},"name":"Croatia","offsetgroup":"Croatia","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.3,0.2,0.1,0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Israel","marker":{"color":"rgb(166,118,29)","pattern":{"shape":""}},"name":"Israel","offsetgroup":"Israel","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","2"],"xaxis":"x","y":[0.2,0.2],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Turkey","marker":{"color":"rgb(102,102,102)","pattern":{"shape":""}},"name":"Turkey","offsetgroup":"Turkey","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.2,0.1,0.1,0.3],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Hungary","marker":{"color":"rgb(27,158,119)","pattern":{"shape":""}},"name":"Hungary","offsetgroup":"Hungary","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.2,0.1,0.1,0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"France","marker":{"color":"rgb(217,95,2)","pattern":{"shape":""}},"name":"France","offsetgroup":"France","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.1,0.1,0.1,0.5],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Georgia","marker":{"color":"rgb(117,112,179)","pattern":{"shape":""}},"name":"Georgia","offsetgroup":"Georgia","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre"],"xaxis":"x","y":[0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Italy","marker":{"color":"rgb(231,41,138)","pattern":{"shape":""}},"name":"Italy","offsetgroup":"Italy","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre"],"xaxis":"x","y":[0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Uzbekistan","marker":{"color":"rgb(102,166,30)","pattern":{"shape":""}},"name":"Uzbekistan","offsetgroup":"Uzbekistan","orientation":"v","showlegend":true,"textposition":"auto","x":["Pre","1","2","3"],"xaxis":"x","y":[0.1,0.2,0.3,0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"India 3","marker":{"color":"rgb(230,171,2)","pattern":{"shape":""}},"name":"India 3","offsetgroup":"India 3","orientation":"v","showlegend":true,"textposition":"auto","x":["1","2","3"],"xaxis":"x","y":[0.5,0.2,0.2],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Romania","marker":{"color":"rgb(166,118,29)","pattern":{"shape":""}},"name":"Romania","offsetgroup":"Romania","orientation":"v","showlegend":true,"textposition":"auto","x":["1"],"xaxis":"x","y":[0.3],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Denmark","marker":{"color":"rgb(102,102,102)","pattern":{"shape":""}},"name":"Denmark","offsetgroup":"Denmark","orientation":"v","showlegend":true,"textposition":"auto","x":["1"],"xaxis":"x","y":[0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Brazil","marker":{"color":"rgb(27,158,119)","pattern":{"shape":""}},"name":"Brazil","offsetgroup":"Brazil","orientation":"v","showlegend":true,"textposition":"auto","x":["1"],"xaxis":"x","y":[0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Serbia","marker":{"color":"rgb(217,95,2)","pattern":{"shape":""}},"name":"Serbia","offsetgroup":"Serbia","orientation":"v","showlegend":true,"textposition":"auto","x":["1","3"],"xaxis":"x","y":[0.1,0.1],"yaxis":"y","type":"bar"},{"alignmentgroup":"True","hovertemplate":"Win %{y}%","legendgroup":"Argentina","marker":{"color":"rgb(117,112,179)","pattern":{"shape":""}},"name":"Argentina","offsetgroup":"Argentina","orientation":"v","showlegend":true,"textposition":"auto","x":["2"],"xaxis":"x","y":[0.1],"yaxis":"y","type":"bar"}],                        {"barmode":"relative","hovermode":"x unified","legend":{"title":{"text":"Country"},"tracegroupgap":0,"traceorder":"reversed"},"margin":{"t":60},"template":{"data":{"barpolar":[{"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"bar":[{"error_x":{"color":"rgb(36,36,36)"},"error_y":{"color":"rgb(36,36,36)"},"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"carpet":[{"aaxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"baxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"type":"carpet"}],"choropleth":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"choropleth"}],"contourcarpet":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"contourcarpet"}],"contour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"contour"}],"heatmapgl":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmapgl"}],"heatmap":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmap"}],"histogram2dcontour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2dcontour"}],"histogram2d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2d"}],"histogram":[{"marker":{"line":{"color":"white","width":0.6}},"type":"histogram"}],"mesh3d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"mesh3d"}],"parcoords":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"parcoords"}],"pie":[{"automargin":true,"type":"pie"}],"scatter3d":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter3d"}],"scattercarpet":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattercarpet"}],"scattergeo":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergeo"}],"scattergl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergl"}],"scattermapbox":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattermapbox"}],"scatterpolargl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolargl"}],"scatterpolar":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolar"}],"scatter":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter"}],"scatterternary":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterternary"}],"surface":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"surface"}],"table":[{"cells":{"fill":{"color":"rgb(237,237,237)"},"line":{"color":"white"}},"header":{"fill":{"color":"rgb(217,217,217)"},"line":{"color":"white"}},"type":"table"}]},"layout":{"annotationdefaults":{"arrowhead":0,"arrowwidth":1},"autotypenumbers":"strict","coloraxis":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"colorscale":{"diverging":[[0.0,"rgb(103,0,31)"],[0.1,"rgb(178,24,43)"],[0.2,"rgb(214,96,77)"],[0.3,"rgb(244,165,130)"],[0.4,"rgb(253,219,199)"],[0.5,"rgb(247,247,247)"],[0.6,"rgb(209,229,240)"],[0.7,"rgb(146,197,222)"],[0.8,"rgb(67,147,195)"],[0.9,"rgb(33,102,172)"],[1.0,"rgb(5,48,97)"]],"sequential":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"sequentialminus":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]]},"colorway":["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD","#8C564B","#E377C2","#7F7F7F","#BCBD22","#17BECF"],"font":{"color":"rgb(36,36,36)"},"geo":{"bgcolor":"white","lakecolor":"white","landcolor":"white","showlakes":true,"showland":true,"subunitcolor":"white"},"hoverlabel":{"align":"left"},"hovermode":"closest","mapbox":{"style":"light"},"paper_bgcolor":"white","plot_bgcolor":"white","polar":{"angularaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","radialaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"scene":{"xaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"zaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"}},"shapedefaults":{"fillcolor":"black","line":{"width":0},"opacity":0.3},"ternary":{"aaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"baxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","caxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"title":{"x":0.05},"xaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"}}},"title":{"text":"Probability of Winning Chess Olympiad | Pawnalyze.com"},"xaxis":{"anchor":"y","domain":[0.0,1.0],"title":{"text":"Round"}},"yaxis":{"anchor":"x","domain":[0.0,1.0],"range":[0,100],"title":{"text":"Win %"}}},                        {"responsive": true}                    )                };                            </script>        </div>


| Country                  |   Win % |
|:-------------------------|--------:|
| United States of America |    62.7 |
| India                    |     7.8 |
| Spain                    |     5.6 |
| Poland                   |     4.8 |
| Azerbaijan               |     4.6 |
| Netherlands              |     3.8 |
| Norway                   |     2.3 |
| Ukraine                  |     2.0 |
| India 2                  |     1.5 |
| England                  |     1.5 |
| Germany                  |     0.9 |
| Armenia                  |     0.6 |
| France                   |     0.5 |
| Iran                     |     0.5 |
| Turkey                   |     0.3 |
| India 3                  |     0.2 |
| Croatia                  |     0.1 |
| Uzbekistan               |     0.1 |
| Serbia                   |     0.1 |
| Hungary                  |     0.1 |
{: .field .narrow}
<br>
Follow me on [Twitter][twit] and be the first to know when I update this page!


[wiki]: https://en.wikipedia.org/wiki/Candidates_Tournament_2022
[twit]: https://twitter.com/pawnalyze
[regs]: https://handbook.fide.com/files/handbook/Regulations_for_the_FIDE_Candidates_Tournament_2022.pdf
[bullet]: https://twitter.com/pawnalyze/status/1542350916409405441?s=20&t=qSrsX6mLumfQwBMFhet1mQ
[model]: https://pawnalyze.com/tournament/2022/02/27/Elo-Rating-Accuracy-Is-Machine-Learning-Better.html
[cand]: tournaments/2022-candidates-tournament/index.md