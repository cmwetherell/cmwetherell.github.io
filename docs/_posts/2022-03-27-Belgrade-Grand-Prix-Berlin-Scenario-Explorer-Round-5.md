---
layout: post
title:  "FIDE Grand Prix Berlin 'What If?' Simulations After Round 5"
date:   2022-03-27 16:00:00 -0700
categories: Tournament
---
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<style>
    .w1, .w2, .w3, .w4, .w5, .w6, .w7, .w8, .w9, .w10, .w11, .w12, .w13, .w14, .w15, .w16 {display: none; overflow: hidden;}
    .d1, .d2, .d3, .d4, .d5, .d6, .d7, .d8, .d9, .d10, .d11, .d12, .d13, .d14, .d15, .d16 {display: none; overflow: hidden;}
    .b1, .b2, .b3, .b4, .b5, .b6, .b7, .b8, .b9, .b10, .b11, .b12, .b13, .b14, .b15, .b16 {display: none; overflow: hidden;}

    .curr {display: none}

    table th, table td { padding: 5px 5px; }
</style>

<script>

    $(document).ready(function(){
        $('input[type="checkbox"]').click(function(){
            var inputValue = $(this).attr("value");
            console.log(inputValue)
            $("." + inputValue).toggle(); 
        });
    });

    $(document).ready(function(){
        $('input:checkbox').click(function(){
            var checkedBoxID = $('input:checkbox:checked').not(this).attr("value");
            console.log(checkedBoxID)
            $("." + checkedBoxID).toggle();
            $('input:checkbox').not(this).prop('checked', false);
        });
    });

</script>

### A glimpse at tomorrow's games

If you follow any major sports league, you are familiar with rooting for a team and hoping some seemingly unrelated result occurs so that your team can advance. For example, if you live in the US you were hoping El Salvador could beat Costa Rica today... well that didn't happen. It's a good thing the USMNT is beating Panama so thoroughly at the moment. What's the cross section between footie and chess fans? I better get back on track!

My point was that you can use this page to see what results you should be rooting for in tomorrow's games. With just one round left, we can clearly see the impact each game has on everyone's chances to qualify for the Candidate's tournament.

The full dataset is 250,000 simulations and when you pick a scenario you get a subset of the data. Each subset of simulations should be fairly credible.

Go ahead and press some buttons. 

**Scenario Picker:**

| White Wins | Draw | Black Wins |
|------------------------|:-------:|----------------------|
| <input type="checkbox" value="w1"/> Andrey Esipenko |<input type="checkbox" value="d1"/> | <input type="checkbox" value="b1"/> Hikaru Nakamura|
| <input type="checkbox" value="w2"/> Anish Giri |<input type="checkbox" value="d2"/> | <input type="checkbox" value="b2"/> Amin Tabatabaei|
| <input type="checkbox" value="w3"/> Daniil Dubov |<input type="checkbox" value="d3"/> | <input type="checkbox" value="b3"/> Shakhriyar Mamedyarov|
| <input type="checkbox" value="w4"/> Grigoriy Oparin |<input type="checkbox" value="d4"/> | <input type="checkbox" value="b4"/> Levon Aronian|
| <input type="checkbox" value="w5"/> Sam Shankland |<input type="checkbox" value="d5"/> | <input type="checkbox" value="b5"/> Maxime Vachier-Lagrave|
| <input type="checkbox" value="w6"/> Vincent Keymer |<input type="checkbox" value="d6"/> | <input type="checkbox" value="b6"/> Leinier Dominguez|
| <input type="checkbox" value="w7"/> Wesley So |<input type="checkbox" value="d7"/> | <input type="checkbox" value="b7"/> Alexandr Predke|
| <input type="checkbox" value="w8"/> Yu Yangyi |<input type="checkbox" value="d8"/> | <input type="checkbox" value="b8"/> Nikita Vitiugov|


**Candidate Qualification Odds**

**White Wins:** Andrey Esipenko vs. Hikaru Nakamura
{: .w1}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |     100.0 |                 20.0 |
| Levon Aronian     |      50.4 |                 19.3 |
| Wesley So         |      14.1 |                 12.8 |
| Anish Giri        |      12.8 |                 12.7 |
| Leinier Dominguez |      11.2 |                 13.1 |
| Hikaru Nakamura   |      10.7 |                 16.4 |
| Sam Shankland     |       0.8 |                  8.5 |
{: .w1}

**Draw:** Andrey Esipenko vs. Hikaru Nakamura
{: .d1}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.8 |                 20.0 |
| Hikaru Nakamura        |      40.4 |                 18.8 |
| Levon Aronian          |      29.9 |                 17.3 |
| Leinier Dominguez      |      13.0 |                 13.9 |
| Anish Giri             |      11.5 |                 12.8 |
| Wesley So              |       5.8 |                 12.1 |
| Sam Shankland          |       0.4 |                  8.8 |
| Maxime Vachier-Lagrave |       0.3 |                  8.6 |
{: .d1}

**Black Wins:** Andrey Esipenko vs. Hikaru Nakamura
{: .b1}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      97.1 |                 20.0 |
| Hikaru Nakamura   |      85.7 |                 22.2 |
| Levon Aronian     |       5.9 |                 14.5 |
| Leinier Dominguez |       5.7 |                 13.4 |
| Anish Giri        |       5.1 |                 12.4 |
| Wesley So         |       0.6 |                 12.0 |
| Sam Shankland     |       0.0 |                  9.2 |
{: .b1}

**White Wins:** Anish Giri vs. Amin Tabatabaei
{: .w2}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      97.6 |                 20.0 |
| Hikaru Nakamura   |      40.4 |                 19.0 |
| Levon Aronian     |      26.6 |                 16.9 |
| Anish Giri        |      17.9 |                 15.4 |
| Leinier Dominguez |      11.0 |                 13.7 |
| Wesley So         |       6.0 |                 11.9 |
| Sam Shankland     |       0.4 |                  9.0 |
{: .w2}

**Draw:** Anish Giri vs. Amin Tabatabaei
{: .d2}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.7 |                 20.0 |
| Hikaru Nakamura        |      41.0 |                 18.6 |
| Levon Aronian          |      35.2 |                 17.8 |
| Leinier Dominguez      |      10.9 |                 13.4 |
| Wesley So              |       7.4 |                 12.0 |
| Anish Giri             |       4.9 |                 11.2 |
| Sam Shankland          |       0.5 |                  8.8 |
| Maxime Vachier-Lagrave |       0.3 |                  8.7 |
{: .d2}

**Black Wins:** Anish Giri vs. Amin Tabatabaei
{: .b2}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      99.9 |                 20.0 |
| Hikaru Nakamura   |      49.1 |                 19.2 |
| Levon Aronian     |      31.4 |                 17.0 |
| Wesley So         |      10.5 |                 14.4 |
| Leinier Dominguez |       9.0 |                 13.1 |
| Sam Shankland     |       0.1 |                  8.0 |
{: .b2}

**White Wins:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .w3}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.1 |                 20.0 |
| Hikaru Nakamura        |      39.7 |                 19.2 |
| Levon Aronian          |      27.4 |                 17.2 |
| Leinier Dominguez      |      17.6 |                 15.4 |
| Anish Giri             |       8.7 |                 12.0 |
| Wesley So              |       6.7 |                 12.5 |
| Sam Shankland          |       0.4 |                  8.6 |
| Maxime Vachier-Lagrave |       0.4 |                  8.6 |
{: .w3}

**Draw:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .d3}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.4 |                 20.0 |
| Hikaru Nakamura        |      40.3 |                 18.9 |
| Levon Aronian          |      30.1 |                 17.2 |
| Anish Giri             |      12.0 |                 13.2 |
| Leinier Dominguez      |      11.6 |                 13.8 |
| Wesley So              |       7.2 |                 12.2 |
| Sam Shankland          |       0.3 |                  8.8 |
| Maxime Vachier-Lagrave |       0.1 |                  8.6 |
{: .d3}

**Black Wins:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .b3}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      99.2 |                 20.0 |
| Hikaru Nakamura   |      45.8 |                 18.7 |
| Levon Aronian     |      33.6 |                 17.4 |
| Anish Giri        |       8.2 |                 12.0 |
| Wesley So         |       7.4 |                 12.3 |
| Leinier Dominguez |       5.1 |                 11.9 |
| Sam Shankland     |       0.6 |                  8.9 |
{: .b3}

**White Wins:** Grigoriy Oparin vs. Levon Aronian
{: .w4}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      96.5 |                 20.0 |
| Hikaru Nakamura   |      86.0 |                 22.4 |
| Anish Giri        |       7.9 |                 13.5 |
| Leinier Dominguez |       7.8 |                 13.4 |
| Wesley So         |       1.7 |                 13.5 |
| Sam Shankland     |       0.0 |                  8.0 |
{: .w4}

**Draw:** Grigoriy Oparin vs. Levon Aronian
{: .d4}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      98.2 |                 20.0 |
| Hikaru Nakamura   |      44.0 |                 19.3 |
| Levon Aronian     |      26.8 |                 16.8 |
| Anish Giri        |      12.3 |                 13.8 |
| Leinier Dominguez |      11.0 |                 13.9 |
| Wesley So         |       7.2 |                 12.5 |
| Sam Shankland     |       0.4 |                  8.7 |
{: .d4}

**Black Wins:** Grigoriy Oparin vs. Levon Aronian
{: .b4}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.6 |                 20.0 |
| Levon Aronian          |      39.6 |                 18.6 |
| Hikaru Nakamura        |      31.6 |                 17.8 |
| Leinier Dominguez      |      11.0 |                 13.2 |
| Anish Giri             |       9.3 |                 11.7 |
| Wesley So              |       8.1 |                 11.8 |
| Sam Shankland          |       0.5 |                  9.0 |
| Maxime Vachier-Lagrave |       0.3 |                  8.6 |
{: .b4}

**White Wins:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .w5}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      97.8 |                 20.0 |
| Hikaru Nakamura   |      44.7 |                 19.2 |
| Levon Aronian     |      25.9 |                 17.2 |
| Anish Giri        |      15.5 |                 14.0 |
| Leinier Dominguez |      12.0 |                 14.0 |
| Wesley So         |       3.0 |                 10.4 |
| Sam Shankland     |       1.1 |                 10.4 |
{: .w5}

**Draw:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .d5}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      98.6 |                 20.0 |
| Hikaru Nakamura   |      47.5 |                 19.3 |
| Levon Aronian     |      27.5 |                 16.7 |
| Leinier Dominguez |      10.2 |                 13.4 |
| Anish Giri        |       9.1 |                 12.6 |
| Wesley So         |       6.7 |                 12.6 |
| Sam Shankland     |       0.4 |                  8.9 |
{: .d5}

**Black Wins:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .b5}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.8 |                 20.0 |
| Levon Aronian          |      41.5 |                 18.5 |
| Hikaru Nakamura        |      26.6 |                 17.5 |
| Wesley So              |      11.3 |                 13.0 |
| Leinier Dominguez      |      11.0 |                 13.4 |
| Anish Giri             |       9.4 |                 11.9 |
| Maxime Vachier-Lagrave |       0.5 |                  9.9 |
| Sam Shankland          |       0.0 |                  7.3 |
{: .b5}

**White Wins:** Vincent Keymer vs. Leinier Domínguez
{: .w6}

| Name            |   Qualify |   Expected GP Points |
|:----------------|----------:|---------------------:|
| Richard Rapport |      99.3 |                 20.0 |
| Hikaru Nakamura |      50.4 |                 18.9 |
| Levon Aronian   |      32.4 |                 17.8 |
| Anish Giri      |      11.2 |                 12.5 |
| Wesley So       |       6.1 |                 12.1 |
| Sam Shankland   |       0.6 |                  9.1 |
{: .w6}

**Draw:** Vincent Keymer vs. Leinier Domínguez
{: .d6}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      98.6 |                 20.0 |
| Hikaru Nakamura   |      46.1 |                 19.0 |
| Levon Aronian     |      30.2 |                 17.0 |
| Anish Giri        |       9.0 |                 12.6 |
| Wesley So         |       8.5 |                 12.5 |
| Leinier Dominguez |       7.4 |                 13.2 |
| Sam Shankland     |       0.2 |                  8.7 |
{: .d6}

**Black Wins:** Vincent Keymer vs. Leinier Domínguez
{: .b6}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.8 |                 20.0 |
| Hikaru Nakamura        |      34.0 |                 18.7 |
| Levon Aronian          |      30.7 |                 17.4 |
| Leinier Dominguez      |      17.9 |                 15.3 |
| Anish Giri             |      11.8 |                 12.8 |
| Wesley So              |       5.9 |                 12.1 |
| Sam Shankland          |       0.6 |                  8.8 |
| Maxime Vachier-Lagrave |       0.3 |                  8.5 |
{: .b6}

**White Wins:** Wesley So vs. Alexandr Predke
{: .w7}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      98.4 |                 20.0 |
| Hikaru Nakamura   |      48.5 |                 19.5 |
| Levon Aronian     |      24.8 |                 16.5 |
| Leinier Dominguez |      10.4 |                 13.6 |
| Anish Giri        |       9.2 |                 12.7 |
| Wesley So         |       8.6 |                 13.7 |
| Sam Shankland     |       0.0 |                  7.9 |
{: .w7}

**Draw:** Wesley So vs. Alexandr Predke
{: .d7}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      99.6 |                 20.0 |
| Levon Aronian     |      38.3 |                 18.1 |
| Hikaru Nakamura   |      32.9 |                 18.1 |
| Anish Giri        |      10.7 |                 12.3 |
| Leinier Dominguez |      10.0 |                 13.2 |
| Wesley So         |       8.0 |                 12.4 |
| Sam Shankland     |       0.7 |                  9.0 |
{: .d7}

**Black Wins:** Wesley So vs. Alexandr Predke
{: .b7}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.9 |                 20.0 |
| Hikaru Nakamura        |      40.2 |                 18.6 |
| Levon Aronian          |      32.2 |                 17.8 |
| Anish Giri             |      14.0 |                 13.7 |
| Leinier Dominguez      |      13.6 |                 13.9 |
| Sam Shankland          |       1.1 |                 11.5 |
| Maxime Vachier-Lagrave |       0.9 |                  7.5 |
| Wesley So              |       0.0 |                  6.8 |
{: .b7}

**White Wins:** Yu Yangyi vs. Nikita Vitiugov
{: .w8}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.3 |                 20.0 |
| Hikaru Nakamura        |      42.6 |                 18.6 |
| Levon Aronian          |      35.5 |                 17.6 |
| Leinier Dominguez      |       9.7 |                 13.3 |
| Wesley So              |       7.0 |                 11.9 |
| Anish Giri             |       5.1 |                 11.2 |
| Sam Shankland          |       0.4 |                  8.9 |
| Maxime Vachier-Lagrave |       0.2 |                  8.6 |
{: .w8}

**Draw:** Yu Yangyi vs. Nikita Vitiugov
{: .d8}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.6 |                 20.0 |
| Hikaru Nakamura        |      40.8 |                 18.9 |
| Levon Aronian          |      28.3 |                 17.2 |
| Anish Giri             |      13.9 |                 13.5 |
| Leinier Dominguez      |      10.4 |                 13.3 |
| Wesley So              |       7.5 |                 12.4 |
| Sam Shankland          |       0.3 |                  8.7 |
| Maxime Vachier-Lagrave |       0.1 |                  8.6 |
{: .d8}

**Black Wins:** Yu Yangyi vs. Nikita Vitiugov
{: .b8}

| Name              |   Qualify |   Expected GP Points |
|:------------------|----------:|---------------------:|
| Richard Rapport   |      98.4 |                 20.0 |
| Hikaru Nakamura   |      42.6 |                 19.0 |
| Levon Aronian     |      29.8 |                 17.0 |
| Leinier Dominguez |      12.7 |                 14.2 |
| Anish Giri        |       9.5 |                 12.8 |
| Wesley So         |       6.5 |                 12.5 |
| Sam Shankland     |       0.6 |                  8.8 |
{: .b8}

