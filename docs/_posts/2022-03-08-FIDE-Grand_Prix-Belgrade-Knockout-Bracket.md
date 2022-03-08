---
layout: post
title:  "FIDE Grand Prix Belgrade Knockout Interactive Bracket"
date:   2022-03-08 00:00:00 -0800
categories: Tournament
---
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="{{ base.url | prepend: site.url }}/assets/bracket.js"></script>

### March Madness is here!

Sorry about the chessy bracket joke. Sorry about the cheesy chess pun. I'm excited to share this bracket. It's just a few numbers that I could have printed in a table below. But, what fun is that? It's much more fun if there's some buttons you can click. And I had fun making it, too. Is this the world's first clickable chess bracket?

On Wednesday, the knockout stage of the FIDE Grand Prix Leg 2 begins in Belgrade, and there are four players remaining: Giri will face Andreikin, and Rapport will take on Vachier-Lagrave. Giri is a 2-to-1 favorite over Andreikin, while Rapport and MVL are closely matched.  Each pair will play two classical games and will switch sides each game. If they are tied after those classical games they go to two Rapid games, then two Blitz games, and finally an Armageddon.

All four players have eared seven Grand Prix Points, and they win three points for winning round one of the knockouts, and an additional three points for winning the tournament. You can also check out current odds for [qualifying into the Candidate's tournament][odds].

The odds below are based on the live Elo ratings from [2700 Chess][2700] and a total of 100,000 simulations.

**Belgrade Knockout Bracket**
<div class="bracket">
    <section class="round semifinals">
        <div class="winners">
            <div class="matchups">
                <div class="matchup">
                    <div class="participants">
                        <div id="anish" class="participant curs winner" onclick="gaClick(this)"><span>Anish Giri</span><span class = "rSpan">66.1%</span></div>
                        <div id="dmitry" class="participant curs" onclick="gaClick(this)"><span>Dmitry Andreikin</span><span  id="dmitry" class = "rSpan">33.9%</span></div>
                    </div>
                </div>
                <div class="matchup">
                    <div class="participants">
                        <div id = "richard" class="participant curs winner" onclick="rmClick(this)"><span>Richard Rapport</span><span class = "rSpan">47.8%</span></div>
                        <div id = "maxime" class="participant curs" onclick="rmClick(this)"><span>Maxime Vachier-Lagrave</span><span class = "rSpan">52.2%</span></div>
                    </div>
                </div>
            </div>
            <div class="connector">
                <div class="merger"></div>
                <div class="line"></div>
            </div>
        </div>
    </section>
    <section class="round finals">
        <div class="winners">
            <div class="matchups">
                <div class="matchup">
									  <div class="begin participants">
                        <div class="participant winner"><span></span><span class = "rSpan"></span></div>
                        <div class="participant"><span></span><span class = "rSpan"></span></div>
									</div>
                    <div class="ar participants">
                        <div class="participant winner"><span>Anish Giri</span><span class = "rSpan">52.6%</span></div>
                        <div class="participant"><span>Richard Rapport</span><span class = "rSpan">47.4%</span></div>
                    </div>
									  <div class="dr participants">
                        <div class="participant winner"><span>Dmitry Andreikin</span><span class = "rSpan">37.7%</span></div>
                        <div class="participant"><span>Richard Rapport</span><span class = "rSpan">62.3%</span></div>
                    </div>
									  <div class="am participants">
                        <div class="participant winner"><span>Anish Giri</span><span class = "rSpan">52.1%</span></div>
                        <div class="participant"><span>Maxime Vachier-Lagrave</span><span class = "rSpan">47.9%</span></div>
                    </div>
									  <div class="dm participants">
                        <div class="participant winner"><span>Dmitry Andreikin</span><span class = "rSpan">34.6%</span></div>
                        <div class="participant"><span>Maxime Vachier-Lagrave</span><span class = "rSpan">65.4%</span></div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</div>

[2700]: https://www.2700chess.com/
[odds]: /tournament/2022/03/07/Belgrade-Grand-Prix-Knockout-Stage-Odds.html