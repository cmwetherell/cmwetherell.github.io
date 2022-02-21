---
layout: post
title:  "Nakamura likely to qualify for 2022 Candidates Tournament from FIDE Grand Prix"
date:   2022-02-20 23:00:00 -0800
categories: Tournament
---
### Who will qualify?

After Hikaru Nakamura's excellent performance during the first leg of the FIDE Grand Prix 2022, the chess world began to speculate about his potential qualification into the 2022 Candidates Tournament. This post summarizes the results of 300,000 simulations of the remaining Grand Prix legs. I wasn't sure how to simulate whether or not Hikaru will try to give his spot to Ding Liren, so for now, we'll leave that aside.

I'll get straight to the results, and, if you care, my thoughts are below.

**Odds of qualifying for 2022 Candidates Tournament**

| Name                   | Qualify % | ELO  |
| ---------------------- | --------- | ---- |
| Hikaru Nakamura        | 52.1      | 2750 |
| Levon Aronian          | 35.8      | 2785 |
| Anish Giri             | 21.9      | 2771 |
| Shakhriyar Mamedyarov  | 20.6      | 2776 |
| Maxime Vachier-Lagrave | 14.9      | 2761 |
| Wesley So              | 14.0      | 2778 |
| Richárd Rapport        | 11.5      | 2762 |
| Leinier Domínguez      | 10.0      | 2756 |
| Dmitry Andreikin       | 4.4       | 2724 |
| Nikita Vitiugov        | 3.9       | 2726 |
| Yu Yangyi              | 3.4       | 2713 |
| Alexander Grischuk     | 2.6       | 2758 |
| Sam Shankland          | 1.5       | 2704 |
| Daniil Dubov           | 1.1       | 2711 |
| Vidit Gujrathi         | 0.8       | 2723 |
| Vladimir Fedoseev      | 0.5       | 2704 |
| Alexandr Predke        | 0.4       | 2682 |
| Pentala Harikrishna    | 0.4       | 2716 |
| Amin Tabatabae         | 0.0       | 2623 |
| Alexei Shirov          | 0.0       | 2704 |
| Grigoriy Oparin        | 0.0       | 2681 |
| Étienne Bacrot         | 0.0       | 2642 |
| Vincent Keymer         | 0.0       | 2664 |

*Note: Anyone that shows up on this table qualified in at least one simulation. E.g., Keymer qualified in 6 of the 300,000 simulations.*

It should be no surprise that Hikaru is the most likely to qualify. I was expecting something closer to 65-75% when I started building the simulation. The reality is there is a lot of variance in the outcomes of a tournament, and he still needs pick up some points in the third leg to qualify. Levon's performance also positioned him nicely to qualify - if he puts together another solid performance, and all signs are that he will, he has good chances to qualify as well.

Grischuk is notably far down the list given his ELO (thanks to Hikaru!). Third place in his pool certainly didn't do him any favors, and he has an uphill battle to qualification. He needs to win in Belgrade AND get rather lucky from there.

I'll be using my program to explore some other questions in the coming days and weeks. Let me know if there's anything you're interested in seeing.

- Who benefitted from the pool randomization? Who didn't? Is the impact material? Can this tell us anything about tournament design?
- How much would 10 classical ELO points improve a players chances of qualifying for Candidates?
- If a player could choose, would it be better to improve by 10 ELO points in classical or rapid? Lot's of rapid tie breaks occur. I think classical time control improvement is more valuable but we might be surprised how much rapid strength is worth.
- What were Hikaru's chances of qualifying before the event started?

There is still plenty for everyone to fight for, and we'll keep an eye on these odds as the rest of the Grand Prix unfolds. Be sure to check back for frequent updates! I hope to provide updates after each tournament day.


### So what is Pawnalyze?

I'm not quite sure yet - I'll be figuring that out as we go! For now it's just a fun project. I recently started getting into Hockey Analytics as well, and there are great resources providing midseason updates on playoff odds, so why not have the same for chess? (shoutout to [MoneyPuck][moneypuck]!)

### How I created the simulations

There's nothing too complicated - though a few assumptions are required. FIDE Elo ratings don't tell us anything about expected draw probability.  We can use a formula to determine the excpected points score between two players with given ELO ratings (i.e., 1 * P(Win) + 0.5 * P(Draw)). I used the ideas found [here][elo] to estimate draw probabilites for super GMs. The most time consuming bit was probably programming all the tie breaker logic - why do they have to make it so complicated, it would be way better to just let [two random players][tiebreak-rules] fight for the win! /s

There's a couple small things I didn't bother to program.  Rapid and Blitz games are less likely to end in a draw, which has some minor implications - for example, in my simulations, the Blitz tiebreaks probably occur marginally more often than 
they are actually expected to occur. So someone with a Blitz advantage over the field, relative to their Rapid advantage, has very slightly overstated odds above. I also just randomized anytime the simulation winds up in an Armageddon game (fairly unlikely situation). I'm not sure of a fair way to simulate the outcome of Armageddon games.

The ELO's listed won't match official sources. I pulled the latest ELO's from 2700 Chess, and used the February FIDE list for everyone else. For Rapid and Blitz tiebreaks, the simulation does use the appropraite ELO ratings for that time control.

### That's all for now, folks 

Please do come back for updates! Check out the [official tournament website][GP-website], and the [Wikipedia entry for the tournament][GP-wiki], which provides a nice summary of the results to date and future legs/pools.

More detailed data below in case you are interested. To determine the odds of qualifying for the Candidates I also had to calculate the odds of winning the Grand Prix, and of getting second place:


**Odds of winning FIDE Grand Prix 2022**

| Name                   | Win % | ELO  |
| ---------------------- | ----- | ---- |
| Hikaru Nakamura        | 27.7  | 2750 |
| Levon Aronian          | 21.3  | 2785 |
| Anish Giri             | 11.7  | 2771 |
| Shakhriyar Mamedyarov  | 10.8  | 2776 |
| Maxime Vachier-Lagrave | 7.2   | 2761 |
| Wesley So              | 5.7   | 2778 |
| Leinier Domínguez      | 5.1   | 2756 |
| Richárd Rapport        | 4.6   | 2762 |
| Dmitry Andreikin       | 1.9   | 2724 |
| Nikita Vitiugov        | 1.5   | 2726 |
| Yu Yangyi              | 1.3   | 2713 |
| Sam Shankland          | 0.5   | 2704 |
| Daniil Dubov           | 0.2   | 2711 |
| Alexander Grischuk     | 0.2   | 2758 |
| Alexandr Predke        | 0.1   | 2682 |
| Vidit Gujrathi         | 0.1   | 2723 |
| Vladimir Fedoseev      | 0.0   | 2704 |
| Pentala Harikrishna    | 0.0   | 2716 |
| Amin Tabatabae         | 0.0   | 2623 |
| Grigoriy Oparin        | 0.0   | 2681 |

**Odds of placing second in FIDE Grand Prix 2022**

| Name                   | Second % | ELO  |
| ---------------------- | -------- | ---- |
| Hikaru Nakamura        | 24.4     | 2750 |
| Levon Aronian          | 14.5     | 2785 |
| Anish Giri             | 10.2     | 2771 |
| Shakhriyar Mamedyarov  | 9.8      | 2776 |
| Wesley So              | 8.3      | 2778 |
| Maxime Vachier-Lagrave | 7.8      | 2761 |
| Richárd Rapport        | 6.9      | 2762 |
| Leinier Domínguez      | 4.9      | 2756 |
| Dmitry Andreikin       | 2.6      | 2724 |
| Alexander Grischuk     | 2.4      | 2758 |
| Nikita Vitiugov        | 2.4      | 2726 |
| Yu Yangyi              | 2.0      | 2713 |
| Sam Shankland          | 1.0      | 2704 |
| Daniil Dubov           | 0.9      | 2711 |
| Vidit Gujrathi         | 0.7      | 2723 |
| Vladimir Fedoseev      | 0.5      | 2704 |
| Pentala Harikrishna    | 0.4      | 2716 |
| Alexandr Predke        | 0.3      | 2682 |
| Amin Tabatabae         | 0.0      | 2623 |
| Alexei Shirov          | 0.0      | 2704 |
| Étienne Bacrot         | 0.0      | 2642 |
| Grigoriy Oparin        | 0.0      | 2681 |
| Vincent Keymer         | 0.0      | 2664 |

[GP-website]: https://worldchess.com/series/grandprix2022
[GP-wiki]: https://en.wikipedia.org/wiki/FIDE_Grand_Prix_2022
[moneypuck]: https://www.moneypuck.com
[elo]: https://wismuth.com/elo/calculator.html#elo_diff=10&formula=normal
[tiebreak-rules]: https://chess24.com/en/read/news/carlsen-lashes-out-against-fide-for-completely-idiotic-tiebreak-rule