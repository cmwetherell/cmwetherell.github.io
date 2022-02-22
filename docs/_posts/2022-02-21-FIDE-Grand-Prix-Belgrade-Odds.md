---
layout: post
title:  "Mamedyarov, MVL, and Giri are favorites heading into FIDE Grand Prix 2022 Belgrade"
date:   2022-02-21 23:00:00 -0800
categories: Tournament
---

### Welcome to Belgrade

With the first tournament behind us, it's time to look ahead to the [second leg of the FIDE Grand Prix 2022][GP2] which will be held in Belgrade. On Sunday, the [Chief Arbiter held a random drawing][pool-drawing] to slot players into each of four pools. The tournament begins with a double round robin and the winner of each pool advances to the knockout stage where we will see some of the worlds top GM's in 2-game mini matches.

Points will be awarded to the overall Grand Prix standings based on pool and knockout performance, which will set up a final showdown in Berlin few weeks later for the third and final leg of the Grand Prix where the remaining two spots in the 2022 Candidates Tournament will be determined.

### Tournament Odds

Based on the results of 100,000 simulations, Shakhriyar Mamedyarov, Maxime Vachier-Lagrave, and Anish Giri are the odds-on favorite to take home the first place prize. In my latest post on [overall Grand Prix odds][naka-odds], I shared some brief detail on how the simulations work so check that out if you want more information.

**Odds of Winning FIDE Grand Prix 2022 Belgrade**

| Name                   | Win % | Elo  |
| ---------------------- | ---- | ---- |
| Shakhriyar Mamedyarov  | 18.7 | 2776 |
| Maxime Vachier-Lagrave | 16.9 | 2761 |
| Anish Giri             | 16.8 | 2771 |
| Alexander Grischuk     | 11.5 | 2758 |
| Richárd Rapport        | 9.5  | 2762 |
| Yu Yangyi              | 5.0  | 2713 |
| Dmitry Andreikin       | 4.9  | 2724 |
| Nikita Vitiugov        | 3.6  | 2726 |
| Vidit Gujrathi         | 3.2  | 2723 |
| Vladimir Fedoseev      | 2.9  | 2704 |
| Alexei Shirov          | 2.0  | 2704 |
| Pentala Harikrishna    | 2.0  | 2716 |
| Sam Shankland          | 1.5  | 2704 |
| Alexandr Predke        | 0.9  | 2682 |
| Étienne Bacrot         | 0.4  | 2642 |
| Amin Tabatabae         | 0.1  | 2623 |

These results are mostly in line with classical time-control ELO ratings.  However, there is some variation due to pool drawings and rapid and blitz Elo differences not shown in the table above. It will be interesting to see how these odds change after each day of the tournament, and I will be posting new simulations every day as the tournament unfolds.

### Some Tidbits You May Find Interesting

You might wonder if the randomization process mentioned above has a metrial effect on the odds of each player winning the tournament. The short is is no, almost none at all. Richárd Rapport was the most unlucky, having his odds decreased by 0.3% from before the drawing to after the drawing. Pool C, with Rpport, Gujrathi, Fedoseev, and Shirov, is the only pool without a player below 2700.

Mamedyarov benefitted the most. He is a whopping 0.2% more likely to win the tournament from before to after the random drawing of pools. +1 FIDE.

Levon Aronian also benefitted  marginally from the pool randomization. His odds of qualifying to the Candidate's Tournament increased 0.8% due the random drawing. Amazingly, he doesn't even play in Belgrade, and the pool results impacted his odds of qualifying the most of anyone. My speculation is that because he is on the right track to qualify (10 points from leg 1 in Berlin), small changes in the dynamics between other players can have a slightly bigger impact on him than you would expect. Still, 0.8% difference is pretty small.

### What's next?

Tomorrow I will share some interactive graphs that let you explore scenarios for each player's qualification odds. You'll be able to discover that Levon Aronian needs to win his pool in leg 3, otherwise he has to get second in his pool, and even then he only has a 1.8% chance of qualifying! That's just one example - it's fun to poke around! [Thanks Plotly][plotly].


[pool-drawing]: https://www.fide.com/news/1578
[naka-odds]: https://pawnalyze.com/tournament/2022/02/21/nakamura-likely-to-qualify-for-candidates-2022.html
[GP2]: https://chessarena.com/broadcasts/13605
[plotly]: https://plotly.com/

[GP-website]: https://worldchess.com/series/grandprix2022
[GP-wiki]: https://en.wikipedia.org/wiki/FIDE_Grand_Prix_2022
[moneypuck]: https://www.moneypuck.com
[elo]: https://wismuth.com/elo/calculator.html#elo_diff=10&formula=normal
[tiebreak-rules]: https://chess24.com/en/read/news/carlsen-lashes-out-against-fide-for-completely-idiotic-tiebreak-rule