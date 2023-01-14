---
layout: post
title:  "Magnus Carlsen's Quest for 2900 Elo"
shortTitle: 'Magnus 2900'
subtitle: "Tracking progress and probabilities for each tournament"
# date: 2022-04-22 15:00:00 -0700
postImage: /assets/img/magnus-2900.jpg # https://www.flickr.com/photos/fide/51782665101/
imageCaption:  "photo: Niki Riga, FIDE"
---

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 

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
  max-height: 360px;
  padding-top: 0px;
}

.postImage img {
  height: auto;
  max-height: 360px;
}

.caption {
  display: block;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  font-size: 12px;
}
</style>

### An ambitious goal for Magnus

After winning the World Championship match against Ian Nepomniachtchi, Magnus Carlsen commented that he set a goal for himself to achieve a 2900 rating, something never been done before. His rating at the time was 2865. Many would argue he is the greatest chess player to ever live, but there is significant doubt about his ability to achieve an Elo of 2900. This page is dedicated to tracking his progress towards that goal, and estimating the chances that he reaches 2900 in any given tournament.

In the upcoming [Tata Steel][tata], he and 13 other super Gransmasters will battle in the 85th iteration of the "Wimbledon of Chess" held in Wijk aan Zee. The the event begins on January 14, 2023. In a miracle situation, Magnus can win all of his games and surpass 2900.  He'll need to score 9/13 to avoid losing points agaisnt the field with an average Elo 127 points worse than his (and would gain 3 Elo). It's difficult to maintain rating at his level, let alone increase his current rating of 2859. Last year, a [well publicized draw][draw] cost him 4.1 rating points. If he wants to reach 2900, the stakes of every game are high - any draw is a step back!

I ran 100,000 simulations of the [Tata Steel Masters][tata-preds] event and below you can see the likelihood of Magnus ending the event at each Elo. In 100,000 simulations he never won all 13 games. It is possible, but less than 1 in 100,000 chance of it happening. I won't hold my breath. But, he can make progress so check out the interactive graph below to explore how likely it is for him to end at various Elo.

My personal opinion: In 2022, there was tons of young and underrated talent due to the COVID-created slowdown of classical chess. Now, I think these youngsters are more appropriately rated (e.g., Prag is where he was 4 months ago). Given that, I think we might see some significant progress in 2023. There's no science behind this number, but I'm looking for him to get to 2880 this year with good chances to cross 2900 in Tata Steel 2024.

<div>                            <div id="bedbd97a-213c-49b0-8261-26e32a9dd5be" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("bedbd97a-213c-49b0-8261-26e32a9dd5be")) {                    Plotly.newPlot(                        "bedbd97a-213c-49b0-8261-26e32a9dd5be",                        [{"alignmentgroup":"True","hovertemplate":"Elo=%{x}<br>Probability (%)=%{y}<extra></extra>","legendgroup":"","marker":{"color":"#ffb703","pattern":{"shape":""}},"name":"","offsetgroup":"","orientation":"v","showlegend":false,"textposition":"auto","x":[2857,2862,2832,2852,2847,2867,2882,2842,2872,2837,2827,2877,2822,2817,2892,2887,2812,2807,2897],"xaxis":"x","y":[16.54,14.678,2.567,15.797,13.09,10.649,1.128,8.746,6.433,5.294,1.11,2.984,0.407,0.137,0.064,0.333,0.031,0.007,0.005],"yaxis":"y","type":"bar"}],                        {"barmode":"relative","legend":{"title":{"text":"Tata Steel Result"},"tracegroupgap":0},"margin":{"t":60},"template":{"data":{"barpolar":[{"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"bar":[{"error_x":{"color":"rgb(36,36,36)"},"error_y":{"color":"rgb(36,36,36)"},"marker":{"line":{"color":"white","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"carpet":[{"aaxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"baxis":{"endlinecolor":"rgb(36,36,36)","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"rgb(36,36,36)"},"type":"carpet"}],"choropleth":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"choropleth"}],"contourcarpet":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"contourcarpet"}],"contour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"contour"}],"heatmapgl":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmapgl"}],"heatmap":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"heatmap"}],"histogram2dcontour":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2dcontour"}],"histogram2d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"histogram2d"}],"histogram":[{"marker":{"line":{"color":"white","width":0.6}},"type":"histogram"}],"mesh3d":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"type":"mesh3d"}],"parcoords":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"parcoords"}],"pie":[{"automargin":true,"type":"pie"}],"scatter3d":[{"line":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter3d"}],"scattercarpet":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattercarpet"}],"scattergeo":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergeo"}],"scattergl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattergl"}],"scattermapbox":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scattermapbox"}],"scatterpolargl":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolargl"}],"scatterpolar":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterpolar"}],"scatter":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatter"}],"scatterternary":[{"marker":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"type":"scatterternary"}],"surface":[{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"},"colorscale":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"type":"surface"}],"table":[{"cells":{"fill":{"color":"rgb(237,237,237)"},"line":{"color":"white"}},"header":{"fill":{"color":"rgb(217,217,217)"},"line":{"color":"white"}},"type":"table"}]},"layout":{"annotationdefaults":{"arrowhead":0,"arrowwidth":1},"autotypenumbers":"strict","coloraxis":{"colorbar":{"outlinewidth":1,"tickcolor":"rgb(36,36,36)","ticks":"outside"}},"colorscale":{"diverging":[[0.0,"rgb(103,0,31)"],[0.1,"rgb(178,24,43)"],[0.2,"rgb(214,96,77)"],[0.3,"rgb(244,165,130)"],[0.4,"rgb(253,219,199)"],[0.5,"rgb(247,247,247)"],[0.6,"rgb(209,229,240)"],[0.7,"rgb(146,197,222)"],[0.8,"rgb(67,147,195)"],[0.9,"rgb(33,102,172)"],[1.0,"rgb(5,48,97)"]],"sequential":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]],"sequentialminus":[[0.0,"#440154"],[0.1111111111111111,"#482878"],[0.2222222222222222,"#3e4989"],[0.3333333333333333,"#31688e"],[0.4444444444444444,"#26828e"],[0.5555555555555556,"#1f9e89"],[0.6666666666666666,"#35b779"],[0.7777777777777778,"#6ece58"],[0.8888888888888888,"#b5de2b"],[1.0,"#fde725"]]},"colorway":["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD","#8C564B","#E377C2","#7F7F7F","#BCBD22","#17BECF"],"font":{"color":"rgb(36,36,36)"},"geo":{"bgcolor":"white","lakecolor":"white","landcolor":"white","showlakes":true,"showland":true,"subunitcolor":"white"},"hoverlabel":{"align":"left"},"hovermode":"closest","mapbox":{"style":"light"},"paper_bgcolor":"white","plot_bgcolor":"white","polar":{"angularaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","radialaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"scene":{"xaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"zaxis":{"backgroundcolor":"white","gridcolor":"rgb(232,232,232)","gridwidth":2,"linecolor":"rgb(36,36,36)","showbackground":true,"showgrid":false,"showline":true,"ticks":"outside","zeroline":false,"zerolinecolor":"rgb(36,36,36)"}},"shapedefaults":{"fillcolor":"black","line":{"width":0},"opacity":0.3},"ternary":{"aaxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"baxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"},"bgcolor":"white","caxis":{"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside"}},"title":{"x":0.05},"xaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"},"yaxis":{"automargin":true,"gridcolor":"rgb(232,232,232)","linecolor":"rgb(36,36,36)","showgrid":false,"showline":true,"ticks":"outside","title":{"standoff":15},"zeroline":false,"zerolinecolor":"rgb(36,36,36)"}}},"title":{"text":"Chasing 2900: Magnus Elo after Tata Steel Chess Tournament"},"xaxis":{"anchor":"y","domain":[0.0,1.0],"title":{"text":"Elo"}},"yaxis":{"anchor":"x","domain":[0.0,1.0],"title":{"text":"Probability (%)"}}},                        {"responsive": true}                    )                };                            </script>        </div>


### Methodology

Some of you may be familiar with my work publishing [tournament simulations][sims], and the methodology here is very similar. I am using a [machine learning][predict] algorithm to predict the outcome of each game, and simulating the results of the tournament many times so we can estimate the chances of various outcomes (for example, "who will win the Candidates Tournament?", or "what will Magnus' Elo be?"). You can also explore the [Python code][repo], if you are interested. I also have an article on my process to [predict the outcome of chess tournaments][tournament].

[tata]: https://tatasteelchess.com/
[draw]: https://en.chessbase.com/post/geir-sune-ostmoe-draws-magnus-carlsen
[sims]: https://pawnalyze.com/tournaments/2022-candidates-tournament/
[predict]: https://pawnalyze.com/tournament/2022/02/27/Elo-Rating-Accuracy-Is-Machine-Learning-Better.html
[repo]: https://github.com/cmwetherell/cmwetherell.github.io/tree/main/chessSim
[tournament]: https://pawnalyze.com/chess-simulations/2022/06/20/How-Our-Chess-Tournament-Predictions-Work.html
[tata-preds]: https://pawnalyze.com/tournaments/2023-Tata-Steel-Masters-Chess-Tournament/
