---
layout: post
title:  "FIDE Grand Prix Berlin 'What If?' Simulations After Round 4"
date:   2022-03-27 00:00:00 -0700
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

### We can see the future
At least, we can try. I just finished watching The Adam Project on Netflix and I sure hope I don't create any time warps by publishing these what-if scenarios. I'm willing to take the risk.

You can explore how the results of rounds 5 and 6 impact everyone's odds for qualifying to the Candidate's tournament. I am skipping over Pool odds, chances to win this individual tournament, and my 'fancy' graphs. Let's keep it to what we all really care about in this post... who is going to qualify?

The full dataset is 100,000 simulations and when you pick a scenario you get a subset of the data. The subsets are likely to be a bit volatile, but should give you an idea of the impact of various games. For example, if Aronian loses to Espienko he can't qualify for the Candidate's!

Go ahead and press some buttons. 

**Scenario Picker:**

| White Wins | Draw | Black Wins |
|------------------------|:-------:|----------------------|
| <input type="checkbox" value="w1"/> Alexandr Predke |<input type="checkbox" value="d1"/> | <input type="checkbox" value="b1"/> Sam Shankland|
| <input type="checkbox" value="w2"/> Amin Tabatabaei |<input type="checkbox" value="d2"/> | <input type="checkbox" value="b2"/> Yu Yangyi|
| <input type="checkbox" value="w3"/> Andrey Esipenko |<input type="checkbox" value="d3"/> | <input type="checkbox" value="b3"/> Hikaru Nakamura|
| <input type="checkbox" value="w4"/> Anish Giri |<input type="checkbox" value="d4"/> | <input type="checkbox" value="b4"/> Amin Tabatabaei|
| <input type="checkbox" value="w5"/> Daniil Dubov |<input type="checkbox" value="d5"/> | <input type="checkbox" value="b5"/> Vincent Keymer|
| <input type="checkbox" value="w6"/> Daniil Dubov |<input type="checkbox" value="d6"/> | <input type="checkbox" value="b6"/> Shakhriyar Mamedyarov|
| <input type="checkbox" value="w7"/> Grigoriy Oparin |<input type="checkbox" value="d7"/> | <input type="checkbox" value="b7"/> Levon Aronian|
| <input type="checkbox" value="w8"/> Hikaru Nakamura |<input type="checkbox" value="d8"/> | <input type="checkbox" value="b8"/> Grigoriy Oparin|
| <input type="checkbox" value="w9"/> Leinier Dominguez |<input type="checkbox" value="d9"/> | <input type="checkbox" value="b9"/> Shakhriyar Mamedyarov|
| <input type="checkbox" value="w10"/> Levon Aronian |<input type="checkbox" value="d10"/> | <input type="checkbox" value="b10"/> Andrey Esipenko|
| <input type="checkbox" value="w11"/> Maxime Vachier-Lagrave |<input type="checkbox" value="d11"/> | <input type="checkbox" value="b11"/> Wesley So|
| <input type="checkbox" value="w12"/> Nikita Vitiugov |<input type="checkbox" value="d12"/> | <input type="checkbox" value="b12"/> Anish Giri|
| <input type="checkbox" value="w13"/> Sam Shankland |<input type="checkbox" value="d13"/> | <input type="checkbox" value="b13"/> Maxime Vachier-Lagrave|
| <input type="checkbox" value="w14"/> Vincent Keymer |<input type="checkbox" value="d14"/> | <input type="checkbox" value="b14"/> Leinier Dominguez|
| <input type="checkbox" value="w15"/> Wesley So |<input type="checkbox" value="d15"/> | <input type="checkbox" value="b15"/> Alexandr Predke|
| <input type="checkbox" value="w16"/> Yu Yangyi |<input type="checkbox" value="d16"/> | <input type="checkbox" value="b16"/> Nikita Vitiugov|


**Candidate Qualification Odds**

**White Wins:** Alexandr Predke vs. Sam Shankland
{: .w1}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.0 |                 20.0 |
| Levon Aronian          |      28.2 |                 15.5 |
| Hikaru Nakamura        |      26.5 |                 17.9 |
| Leinier Dominguez      |      19.0 |                 15.2 |
| Anish Giri             |      14.9 |                 13.3 |
| Wesley So              |       7.9 |                 10.5 |
| Maxime Vachier-Lagrave |       4.1 |                  9.9 |
| Shakhriyar Mamedyarov  |       0.2 |                  7.2 |
| Sam Shankland          |       0.1 |                  5.3 |
| Nikita Vitiugov        |       0.1 |                  5.7 |
| Alexandr Predke        |       0.0 |                  7.6 |
{: .w1}

**Draw:** Alexandr Predke vs. Sam Shankland
{: .d1}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.8 |                 20.0 |
| Hikaru Nakamura        |      36.2 |                 18.2 |
| Levon Aronian          |      17.9 |                 15.5 |
| Leinier Dominguez      |      15.7 |                 13.8 |
| Maxime Vachier-Lagrave |       9.6 |                 11.5 |
| Anish Giri             |       9.4 |                 11.8 |
| Wesley So              |       9.0 |                  9.4 |
| Shakhriyar Mamedyarov  |       2.1 |                  8.6 |
| Sam Shankland          |       0.6 |                  7.5 |
| Nikita Vitiugov        |       0.5 |                  6.5 |
| Andrey Esipenko        |       0.2 |                  4.7 |
| Alexandr Predke        |       0.2 |                  5.2 |
{: .d1}

**Black Wins:** Alexandr Predke vs. Sam Shankland
{: .b1}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.0 |                 20.0 |
| Hikaru Nakamura        |      42.2 |                 18.0 |
| Anish Giri             |      17.8 |                 13.2 |
| Wesley So              |      11.8 |                 10.2 |
| Leinier Dominguez      |       7.9 |                 12.3 |
| Maxime Vachier-Lagrave |       7.3 |                 11.4 |
| Shakhriyar Mamedyarov  |       6.4 |                 10.8 |
| Levon Aronian          |       4.5 |                 13.8 |
| Sam Shankland          |       1.8 |                  8.8 |
| Nikita Vitiugov        |       1.3 |                  6.2 |
{: .b1}

**White Wins:** Amin Tabatabaei vs. Yu Yangyi
{: .w2}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.5 |                 20.0 |
| Hikaru Nakamura        |      48.9 |                 19.1 |
| Anish Giri             |      14.1 |                 13.9 |
| Leinier Dominguez      |      11.2 |                 13.1 |
| Wesley So              |      11.0 |                 10.0 |
| Levon Aronian          |       6.9 |                 13.3 |
| Shakhriyar Mamedyarov  |       4.6 |                  9.8 |
| Maxime Vachier-Lagrave |       2.7 |                  9.7 |
| Nikita Vitiugov        |       1.6 |                  7.0 |
| Sam Shankland          |       0.8 |                  8.1 |
| Alexandr Predke        |       0.5 |                  5.6 |
{: .w2}

**Draw:** Amin Tabatabaei vs. Yu Yangyi
{: .d2}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.7 |                 20.0 |
| Hikaru Nakamura        |      32.5 |                 18.0 |
| Levon Aronian          |      16.2 |                 15.3 |
| Leinier Dominguez      |      16.1 |                 14.2 |
| Anish Giri             |      14.1 |                 12.7 |
| Wesley So              |       9.7 |                  9.4 |
| Maxime Vachier-Lagrave |       9.1 |                 11.7 |
| Shakhriyar Mamedyarov  |       2.0 |                  8.4 |
| Sam Shankland          |       0.8 |                  7.2 |
| Nikita Vitiugov        |       0.4 |                  6.1 |
| Andrey Esipenko        |       0.3 |                  4.7 |
| Alexandr Predke        |       0.1 |                  5.3 |
{: .d2}

**Black Wins:** Amin Tabatabaei vs. Yu Yangyi
{: .b2}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.9 |                 20.0 |
| Hikaru Nakamura        |      30.9 |                 17.7 |
| Levon Aronian          |      30.0 |                 16.2 |
| Leinier Dominguez      |      17.0 |                 14.0 |
| Maxime Vachier-Lagrave |       8.8 |                 10.8 |
| Wesley So              |       6.7 |                 10.2 |
| Anish Giri             |       5.5 |                 10.8 |
| Shakhriyar Mamedyarov  |       1.0 |                  8.1 |
| Sam Shankland          |       0.1 |                  6.6 |
| Alexandr Predke        |       0.1 |                  5.8 |
| Nikita Vitiugov        |       0.0 |                  6.2 |
{: .b2}

**White Wins:** Andrey Esipenko vs. Hikaru Nakamura
{: .w3}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |     100.0 |                 20.0 |
| Levon Aronian          |      41.0 |                 17.6 |
| Leinier Dominguez      |      18.1 |                 14.2 |
| Wesley So              |      16.8 |                 11.5 |
| Maxime Vachier-Lagrave |       7.9 |                 10.3 |
| Anish Giri             |       7.4 |                 10.7 |
| Hikaru Nakamura        |       5.0 |                 15.1 |
| Shakhriyar Mamedyarov  |       2.8 |                  8.8 |
| Andrey Esipenko        |       0.6 |                  5.9 |
| Sam Shankland          |       0.2 |                  6.6 |
| Nikita Vitiugov        |       0.1 |                  5.9 |
{: .w3}

**Draw:** Andrey Esipenko vs. Hikaru Nakamura
{: .d3}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.1 |                 20.0 |
| Hikaru Nakamura        |      32.6 |                 18.1 |
| Levon Aronian          |      16.6 |                 15.3 |
| Leinier Dominguez      |      15.3 |                 13.7 |
| Anish Giri             |      15.2 |                 13.1 |
| Maxime Vachier-Lagrave |       9.5 |                 11.6 |
| Wesley So              |       6.8 |                  8.9 |
| Shakhriyar Mamedyarov  |       2.8 |                  8.7 |
| Sam Shankland          |       1.0 |                  7.3 |
| Nikita Vitiugov        |       0.8 |                  6.4 |
| Alexandr Predke        |       0.3 |                  5.6 |
{: .d3}

**Black Wins:** Andrey Esipenko vs. Hikaru Nakamura
{: .b3}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.6 |                 20.0 |
| Hikaru Nakamura        |      66.3 |                 21.0 |
| Leinier Dominguez      |      13.8 |                 14.4 |
| Anish Giri             |       8.1 |                 12.2 |
| Wesley So              |       6.3 |                  9.7 |
| Maxime Vachier-Lagrave |       5.0 |                 10.9 |
| Levon Aronian          |       2.5 |                 13.1 |
| Shakhriyar Mamedyarov  |       0.2 |                  8.0 |
| Sam Shankland          |       0.2 |                  7.4 |
| Nikita Vitiugov        |       0.1 |                  6.3 |
{: .b3}

**White Wins:** Anish Giri vs. Amin Tabatabaei
{: .w4}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.6 |                 20.0 |
| Hikaru Nakamura        |      29.6 |                 17.8 |
| Levon Aronian          |      17.6 |                 15.0 |
| Anish Giri             |      16.9 |                 13.7 |
| Leinier Dominguez      |      16.2 |                 14.1 |
| Wesley So              |      11.0 |                 10.1 |
| Maxime Vachier-Lagrave |       6.5 |                 10.5 |
| Shakhriyar Mamedyarov  |       2.3 |                  8.4 |
| Sam Shankland          |       0.7 |                  7.4 |
| Nikita Vitiugov        |       0.5 |                  6.6 |
| Alexandr Predke        |       0.2 |                  5.5 |
{: .w4}

**Draw:** Anish Giri vs. Amin Tabatabaei
{: .d4}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.1 |                 20.0 |
| Hikaru Nakamura        |      40.0 |                 18.4 |
| Levon Aronian          |      24.9 |                 15.9 |
| Leinier Dominguez      |      13.9 |                 13.6 |
| Maxime Vachier-Lagrave |       8.3 |                 11.8 |
| Anish Giri             |       6.0 |                 11.6 |
| Wesley So              |       5.1 |                  9.4 |
| Shakhriyar Mamedyarov  |       1.4 |                  9.0 |
| Sam Shankland          |       0.7 |                  6.8 |
| Nikita Vitiugov        |       0.5 |                  5.4 |
| Alexandr Predke        |       0.1 |                  5.4 |
{: .d4}

**Black Wins:** Anish Giri vs. Amin Tabatabaei
{: .b4}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.9 |                 20.0 |
| Hikaru Nakamura        |      44.7 |                 18.8 |
| Leinier Dominguez      |      16.9 |                 14.3 |
| Maxime Vachier-Lagrave |      14.5 |                 12.2 |
| Levon Aronian          |      10.0 |                 14.8 |
| Wesley So              |       9.6 |                  8.9 |
| Shakhriyar Mamedyarov  |       3.0 |                  7.9 |
| Andrey Esipenko        |       1.2 |                  5.5 |
| Nikita Vitiugov        |       0.2 |                  6.6 |
{: .b4}

**White Wins:** Daniil Dubov vs. Vincent Keymer
{: .w5}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.4 |                 20.0 |
| Hikaru Nakamura        |      29.7 |                 17.8 |
| Levon Aronian          |      26.4 |                 16.1 |
| Leinier Dominguez      |      14.5 |                 13.9 |
| Anish Giri             |      11.3 |                 12.1 |
| Maxime Vachier-Lagrave |       9.3 |                 11.7 |
| Wesley So              |       8.1 |                  9.0 |
| Shakhriyar Mamedyarov  |       0.9 |                  8.9 |
| Sam Shankland          |       0.3 |                  7.4 |
| Nikita Vitiugov        |       0.1 |                  6.3 |
| Alexandr Predke        |       0.0 |                  5.4 |
{: .w5}

**Draw:** Daniil Dubov vs. Vincent Keymer
{: .d5}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.4 |                 20.0 |
| Hikaru Nakamura        |      39.3 |                 18.4 |
| Leinier Dominguez      |      15.4 |                 14.2 |
| Levon Aronian          |      12.8 |                 14.5 |
| Anish Giri             |      12.7 |                 12.9 |
| Wesley So              |       8.9 |                 10.1 |
| Maxime Vachier-Lagrave |       7.1 |                 10.4 |
| Shakhriyar Mamedyarov  |       3.6 |                  8.4 |
| Nikita Vitiugov        |       1.0 |                  6.1 |
| Sam Shankland          |       0.7 |                  7.1 |
| Alexandr Predke        |       0.2 |                  5.8 |
{: .d5}

**Black Wins:** Daniil Dubov vs. Vincent Keymer
{: .b5}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.8 |                 20.0 |
| Hikaru Nakamura        |      36.5 |                 18.1 |
| Leinier Dominguez      |      19.8 |                 13.7 |
| Wesley So              |      12.5 |                 10.8 |
| Levon Aronian          |      11.8 |                 14.8 |
| Anish Giri             |       9.3 |                 11.4 |
| Maxime Vachier-Lagrave |       6.5 |                 11.6 |
| Shakhriyar Mamedyarov  |       1.9 |                  7.7 |
| Sam Shankland          |       1.2 |                  6.5 |
| Andrey Esipenko        |       1.1 |                  5.0 |
| Alexandr Predke        |       0.3 |                  4.9 |
| Nikita Vitiugov        |       0.2 |                  6.6 |
{: .b5}

**White Wins:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .w6}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.4 |                 20.0 |
| Hikaru Nakamura        |      36.8 |                 18.9 |
| Levon Aronian          |      23.2 |                 15.9 |
| Leinier Dominguez      |      20.4 |                 15.5 |
| Anish Giri             |       7.9 |                 11.7 |
| Maxime Vachier-Lagrave |       7.4 |                 11.3 |
| Wesley So              |       5.7 |                 10.2 |
| Sam Shankland          |       0.1 |                  6.1 |
| Alexandr Predke        |       0.1 |                  6.0 |
{: .w6}

**Draw:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .d6}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.2 |                 20.0 |
| Hikaru Nakamura        |      33.8 |                 17.9 |
| Levon Aronian          |      17.8 |                 15.3 |
| Leinier Dominguez      |      17.4 |                 14.1 |
| Anish Giri             |      10.7 |                 12.2 |
| Wesley So              |       9.2 |                  9.8 |
| Maxime Vachier-Lagrave |       7.7 |                 10.8 |
| Shakhriyar Mamedyarov  |       2.5 |                  8.5 |
| Sam Shankland          |       0.8 |                  7.4 |
| Nikita Vitiugov        |       0.7 |                  6.0 |
| Alexandr Predke        |       0.2 |                  5.5 |
{: .d6}

**Black Wins:** Daniil Dubov vs. Shakhriyar Mamedyarov
{: .b6}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.5 |                 20.0 |
| Hikaru Nakamura        |      35.0 |                 18.0 |
| Anish Giri             |      18.1 |                 13.2 |
| Levon Aronian          |      17.8 |                 14.5 |
| Wesley So              |      11.9 |                  9.1 |
| Maxime Vachier-Lagrave |       9.8 |                 12.0 |
| Leinier Dominguez      |       4.6 |                 12.0 |
| Shakhriyar Mamedyarov  |       2.9 |                 11.5 |
| Andrey Esipenko        |       0.8 |                  5.4 |
| Sam Shankland          |       0.3 |                  7.5 |
| Nikita Vitiugov        |       0.2 |                  7.4 |
| Alexandr Predke        |       0.0 |                  5.0 |
{: .b6}

**White Wins:** Grigoriy Oparin vs. Levon Aronian
{: .w7}

| Name                  |   Qualify |   Expected GP Points |
|:----------------------|----------:|---------------------:|
| Richard Rapport       |      99.9 |                 20.0 |
| Hikaru Nakamura       |      52.9 |                 18.0 |
| Wesley So             |      23.6 |                 12.8 |
| Anish Giri            |      10.9 |                 12.1 |
| Leinier Dominguez     |       9.8 |                 12.8 |
| Sam Shankland         |       2.2 |                  8.6 |
| Shakhriyar Mamedyarov |       0.6 |                 10.9 |
| Nikita Vitiugov       |       0.2 |                  6.9 |
{: .w7}

**Draw:** Grigoriy Oparin vs. Levon Aronian
{: .d7}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.6 |                 20.0 |
| Hikaru Nakamura        |      39.6 |                 18.5 |
| Leinier Dominguez      |      17.6 |                 14.1 |
| Anish Giri             |      12.2 |                 12.4 |
| Levon Aronian          |      11.3 |                 14.2 |
| Wesley So              |       8.3 |                  9.4 |
| Maxime Vachier-Lagrave |       7.6 |                 11.3 |
| Shakhriyar Mamedyarov  |       3.2 |                  8.3 |
| Nikita Vitiugov        |       0.7 |                  6.2 |
| Sam Shankland          |       0.6 |                  7.2 |
| Alexandr Predke        |       0.2 |                  5.7 |
{: .d7}

**Black Wins:** Grigoriy Oparin vs. Levon Aronian
{: .b7}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.2 |                 20.0 |
| Levon Aronian          |      35.8 |                 17.9 |
| Hikaru Nakamura        |      21.9 |                 17.5 |
| Leinier Dominguez      |      13.5 |                 14.1 |
| Anish Giri             |      10.7 |                 12.3 |
| Maxime Vachier-Lagrave |      10.6 |                 11.5 |
| Wesley So              |       7.1 |                  9.6 |
| Shakhriyar Mamedyarov  |       0.7 |                  8.4 |
| Andrey Esipenko        |       0.4 |                  5.0 |
| Sam Shankland          |       0.2 |                  6.8 |
| Nikita Vitiugov        |       0.1 |                  6.3 |
{: .b7}

**White Wins:** Hikaru Nakamura vs. Grigoriy Oparin
{: .w8}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.1 |                 20.0 |
| Hikaru Nakamura        |      53.0 |                 20.2 |
| Levon Aronian          |      19.1 |                 15.7 |
| Leinier Dominguez      |      13.6 |                 14.4 |
| Anish Giri             |       6.4 |                 11.8 |
| Wesley So              |       5.0 |                 10.3 |
| Maxime Vachier-Lagrave |       3.8 |                 10.7 |
| Shakhriyar Mamedyarov  |       0.5 |                  7.6 |
| Andrey Esipenko        |       0.3 |                  4.6 |
| Sam Shankland          |       0.1 |                  7.2 |
| Nikita Vitiugov        |       0.1 |                  6.0 |
{: .w8}

**Draw:** Hikaru Nakamura vs. Grigoriy Oparin
{: .d8}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.5 |                 20.0 |
| Levon Aronian          |      24.3 |                 15.6 |
| Hikaru Nakamura        |      21.0 |                 16.7 |
| Leinier Dominguez      |      17.6 |                 13.8 |
| Anish Giri             |      16.7 |                 12.9 |
| Wesley So              |       9.5 |                  8.8 |
| Maxime Vachier-Lagrave |       9.4 |                 11.3 |
| Sam Shankland          |       1.1 |                  7.5 |
| Shakhriyar Mamedyarov  |       0.9 |                  9.2 |
| Alexandr Predke        |       0.1 |                  5.8 |
| Nikita Vitiugov        |       0.0 |                  6.1 |
{: .d8}

**Black Wins:** Hikaru Nakamura vs. Grigoriy Oparin
{: .b8}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |     100.0 |                 20.0 |
| Wesley So              |      22.7 |                 10.6 |
| Maxime Vachier-Lagrave |      19.7 |                 12.1 |
| Leinier Dominguez      |      16.3 |                 13.0 |
| Anish Giri             |      14.4 |                 12.4 |
| Shakhriyar Mamedyarov  |      12.3 |                 10.0 |
| Hikaru Nakamura        |       9.6 |                 14.9 |
| Nikita Vitiugov        |       3.3 |                  7.6 |
| Sam Shankland          |       1.0 |                  6.0 |
| Alexandr Predke        |       0.6 |                  5.3 |
{: .b8}

**White Wins:** Leinier Domínguez vs. Shakhriyar Mamedyarov
{: .w9}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.0 |                 20.0 |
| Hikaru Nakamura        |      31.0 |                 18.5 |
| Leinier Dominguez      |      26.0 |                 16.2 |
| Levon Aronian          |      19.2 |                 15.8 |
| Anish Giri             |      13.3 |                 13.2 |
| Maxime Vachier-Lagrave |       7.5 |                 11.5 |
| Wesley So              |       4.1 |                  9.2 |
| Sam Shankland          |       0.6 |                  6.3 |
| Alexandr Predke        |       0.2 |                  6.3 |
{: .w9}

**Draw:** Leinier Domínguez vs. Shakhriyar Mamedyarov
{: .d9}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.3 |                 20.0 |
| Hikaru Nakamura        |      33.0 |                 17.8 |
| Levon Aronian          |      15.5 |                 14.9 |
| Leinier Dominguez      |      13.7 |                 13.6 |
| Wesley So              |      13.6 |                 10.3 |
| Anish Giri             |      11.7 |                 12.1 |
| Maxime Vachier-Lagrave |       7.7 |                 11.0 |
| Shakhriyar Mamedyarov  |       3.7 |                  9.3 |
| Nikita Vitiugov        |       0.9 |                  6.7 |
| Sam Shankland          |       0.4 |                  7.2 |
| Andrey Esipenko        |       0.3 |                  4.9 |
| Alexandr Predke        |       0.2 |                  5.2 |
{: .d9}

**Black Wins:** Leinier Domínguez vs. Shakhriyar Mamedyarov
{: .b9}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.2 |                 20.0 |
| Hikaru Nakamura        |      46.9 |                 18.3 |
| Levon Aronian          |      29.4 |                 15.4 |
| Maxime Vachier-Lagrave |      10.2 |                 10.9 |
| Anish Giri             |       7.6 |                 11.5 |
| Wesley So              |       3.4 |                  8.7 |
| Sam Shankland          |       1.2 |                  8.6 |
| Leinier Dominguez      |       1.1 |                 10.7 |
| Shakhriyar Mamedyarov  |       0.9 |                 12.1 |
{: .b9}

**White Wins:** Levon Aronian vs. Andrey Esipenko
{: .w10}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.9 |                 20.0 |
| Levon Aronian          |      29.5 |                 16.9 |
| Hikaru Nakamura        |      22.9 |                 17.4 |
| Leinier Dominguez      |      16.4 |                 14.4 |
| Anish Giri             |      11.5 |                 12.5 |
| Wesley So              |      10.1 |                 10.0 |
| Maxime Vachier-Lagrave |       6.4 |                 10.7 |
| Shakhriyar Mamedyarov  |       2.8 |                  8.1 |
| Nikita Vitiugov        |       0.9 |                  5.9 |
| Sam Shankland          |       0.5 |                  7.2 |
| Alexandr Predke        |       0.2 |                  5.5 |
{: .w10}

**Draw:** Levon Aronian vs. Andrey Esipenko
{: .d10}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.3 |                 20.0 |
| Hikaru Nakamura        |      45.4 |                 18.8 |
| Leinier Dominguez      |      16.2 |                 13.7 |
| Levon Aronian          |      13.0 |                 14.6 |
| Anish Giri             |       9.9 |                 11.7 |
| Maxime Vachier-Lagrave |       7.7 |                 11.2 |
| Wesley So              |       6.6 |                  9.2 |
| Shakhriyar Mamedyarov  |       1.0 |                  8.8 |
| Sam Shankland          |       0.9 |                  7.4 |
| Alexandr Predke        |       0.1 |                  5.6 |
| Nikita Vitiugov        |       0.0 |                  6.7 |
{: .d10}

**Black Wins:** Levon Aronian vs. Andrey Esipenko
{: .b10}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.7 |                 20.0 |
| Hikaru Nakamura        |      40.3 |                 18.1 |
| Anish Giri             |      17.8 |                 13.7 |
| Maxime Vachier-Lagrave |      15.1 |                 12.2 |
| Wesley So              |      13.6 |                 10.3 |
| Leinier Dominguez      |      10.7 |                 13.5 |
| Shakhriyar Mamedyarov  |       3.3 |                  9.3 |
| Andrey Esipenko        |       1.2 |                  6.9 |
| Nikita Vitiugov        |       0.3 |                  6.0 |
| Alexandr Predke        |       0.0 |                  5.2 |
{: .b10}

**White Wins:** Maxime Vachier-Lagrave vs. Wesley So
{: .w11}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.6 |                 20.0 |
| Hikaru Nakamura        |      33.1 |                 18.5 |
| Maxime Vachier-Lagrave |      23.9 |                 15.2 |
| Leinier Dominguez      |      15.4 |                 14.1 |
| Anish Giri             |      14.9 |                 12.8 |
| Levon Aronian          |      13.0 |                 15.0 |
| Shakhriyar Mamedyarov  |       1.3 |                  8.7 |
| Sam Shankland          |       0.7 |                  7.3 |
| Wesley So              |       0.1 |                  5.9 |
| Nikita Vitiugov        |       0.1 |                  6.5 |
| Alexandr Predke        |       0.0 |                  5.1 |
{: .w11}

**Draw:** Maxime Vachier-Lagrave vs. Wesley So
{: .d11}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.5 |                 20.0 |
| Hikaru Nakamura        |      35.5 |                 18.0 |
| Levon Aronian          |      21.6 |                 15.6 |
| Leinier Dominguez      |      14.9 |                 13.6 |
| Anish Giri             |      10.4 |                 11.9 |
| Wesley So              |       9.5 |                 10.2 |
| Shakhriyar Mamedyarov  |       3.3 |                  8.7 |
| Maxime Vachier-Lagrave |       3.2 |                 10.2 |
| Nikita Vitiugov        |       0.8 |                  6.3 |
| Sam Shankland          |       0.7 |                  7.4 |
| Andrey Esipenko        |       0.3 |                  4.7 |
| Alexandr Predke        |       0.2 |                  5.6 |
{: .d11}

**Black Wins:** Maxime Vachier-Lagrave vs. Wesley So
{: .b11}

| Name                  |   Qualify |   Expected GP Points |
|:----------------------|----------:|---------------------:|
| Richard Rapport       |      99.0 |                 20.0 |
| Hikaru Nakamura       |      34.0 |                 17.7 |
| Wesley So             |      19.5 |                 13.3 |
| Levon Aronian         |      19.3 |                 14.7 |
| Leinier Dominguez     |      17.6 |                 14.7 |
| Anish Giri            |      10.2 |                 12.7 |
| Shakhriyar Mamedyarov |       0.2 |                  8.0 |
| Sam Shankland         |       0.1 |                  6.5 |
| Nikita Vitiugov       |       0.0 |                  6.0 |
{: .b11}

**White Wins:** Nikita Vitiugov vs. Anish Giri
{: .w12}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |     100.0 |                 20.0 |
| Hikaru Nakamura        |      28.3 |                 17.5 |
| Levon Aronian          |      24.1 |                 15.8 |
| Leinier Dominguez      |      16.8 |                 13.8 |
| Wesley So              |      15.8 |                 10.4 |
| Maxime Vachier-Lagrave |       8.9 |                 10.8 |
| Shakhriyar Mamedyarov  |       3.8 |                  8.6 |
| Nikita Vitiugov        |       1.3 |                  9.8 |
| Sam Shankland          |       0.7 |                  7.6 |
| Alexandr Predke        |       0.4 |                  5.3 |
{: .w12}

**Draw:** Nikita Vitiugov vs. Anish Giri
{: .d12}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.9 |                 20.0 |
| Hikaru Nakamura        |      40.1 |                 18.5 |
| Levon Aronian          |      16.4 |                 14.8 |
| Leinier Dominguez      |      15.3 |                 13.8 |
| Anish Giri             |      11.1 |                 12.3 |
| Maxime Vachier-Lagrave |       9.0 |                 11.5 |
| Wesley So              |       6.3 |                  9.2 |
| Shakhriyar Mamedyarov  |       1.7 |                  8.6 |
| Sam Shankland          |       0.5 |                  6.9 |
| Nikita Vitiugov        |       0.3 |                  5.7 |
| Andrey Esipenko        |       0.2 |                  4.7 |
| Alexandr Predke        |       0.1 |                  5.9 |
{: .d12}

**Black Wins:** Nikita Vitiugov vs. Anish Giri
{: .b12}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      97.8 |                 20.0 |
| Anish Giri             |      25.7 |                 15.6 |
| Hikaru Nakamura        |      23.5 |                 17.3 |
| Levon Aronian          |      20.9 |                 16.2 |
| Leinier Dominguez      |      15.3 |                 14.7 |
| Wesley So              |      10.6 |                 10.7 |
| Maxime Vachier-Lagrave |       3.9 |                 10.4 |
| Shakhriyar Mamedyarov  |       1.7 |                  8.2 |
| Sam Shankland          |       0.6 |                  7.5 |
{: .b12}

**White Wins:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .w13}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.3 |                 20.0 |
| Hikaru Nakamura        |      36.6 |                 18.2 |
| Levon Aronian          |      26.9 |                 15.5 |
| Anish Giri             |      16.8 |                 13.7 |
| Leinier Dominguez      |      12.0 |                 13.6 |
| Wesley So              |       7.2 |                  9.2 |
| Sam Shankland          |       1.7 |                  9.6 |
| Shakhriyar Mamedyarov  |       0.1 |                  9.4 |
| Maxime Vachier-Lagrave |       0.1 |                  8.1 |
{: .w13}

**Draw:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .d13}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.7 |                 20.0 |
| Hikaru Nakamura        |      30.8 |                 17.8 |
| Levon Aronian          |      18.5 |                 15.4 |
| Leinier Dominguez      |      17.5 |                 13.9 |
| Wesley So              |      11.5 |                  9.9 |
| Anish Giri             |       9.3 |                 11.3 |
| Maxime Vachier-Lagrave |       7.8 |                 11.0 |
| Shakhriyar Mamedyarov  |       3.2 |                  8.4 |
| Nikita Vitiugov        |       0.7 |                  7.0 |
| Andrey Esipenko        |       0.3 |                  4.9 |
| Sam Shankland          |       0.3 |                  7.2 |
| Alexandr Predke        |       0.3 |                  5.6 |
{: .d13}

**Black Wins:** Sam Shankland vs. Maxime Vachier-Lagrave
{: .b13}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.2 |                 20.0 |
| Hikaru Nakamura        |      38.6 |                 18.5 |
| Leinier Dominguez      |      15.9 |                 14.4 |
| Maxime Vachier-Lagrave |      15.9 |                 14.2 |
| Levon Aronian          |      11.6 |                 14.9 |
| Anish Giri             |      10.4 |                 12.6 |
| Wesley So              |       6.7 |                  9.9 |
| Shakhriyar Mamedyarov  |       2.2 |                  7.9 |
| Nikita Vitiugov        |       0.5 |                  5.8 |
{: .b13}

**White Wins:** Vincent Keymer vs. Leinier Domínguez
{: .w14}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.9 |                 20.0 |
| Hikaru Nakamura        |      34.4 |                 17.8 |
| Levon Aronian          |      16.8 |                 15.2 |
| Leinier Dominguez      |      13.2 |                 12.5 |
| Maxime Vachier-Lagrave |      10.6 |                 10.8 |
| Shakhriyar Mamedyarov  |       9.2 |                  7.8 |
| Anish Giri             |       5.7 |                 10.3 |
| Wesley So              |       3.9 |                  8.0 |
| Nikita Vitiugov        |       3.1 |                  7.7 |
| Sam Shankland          |       2.2 |                  8.2 |
| Alexandr Predke        |       0.7 |                  6.4 |
{: .w14}

**Draw:** Vincent Keymer vs. Leinier Domínguez
{: .d14}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.9 |                 20.0 |
| Hikaru Nakamura        |      35.7 |                 18.1 |
| Levon Aronian          |      16.0 |                 14.8 |
| Leinier Dominguez      |      14.3 |                 13.8 |
| Anish Giri             |      14.1 |                 12.8 |
| Wesley So              |      10.1 |                  9.7 |
| Maxime Vachier-Lagrave |       8.6 |                 11.4 |
| Shakhriyar Mamedyarov  |       1.5 |                  8.9 |
| Sam Shankland          |       0.4 |                  6.9 |
| Andrey Esipenko        |       0.2 |                  4.9 |
| Nikita Vitiugov        |       0.1 |                  6.0 |
| Alexandr Predke        |       0.1 |                  5.5 |
{: .d14}

**Black Wins:** Vincent Keymer vs. Leinier Domínguez
{: .b14}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.4 |                 20.0 |
| Hikaru Nakamura        |      31.6 |                 18.2 |
| Levon Aronian          |      27.6 |                 16.5 |
| Leinier Dominguez      |      20.3 |                 15.2 |
| Wesley So              |       8.9 |                 10.6 |
| Anish Giri             |       7.9 |                 12.1 |
| Maxime Vachier-Lagrave |       5.0 |                 10.5 |
| Sam Shankland          |       0.2 |                  7.4 |
| Nikita Vitiugov        |       0.0 |                  6.0 |
{: .b14}

**White Wins:** Wesley So vs. Alexandr Predke
{: .w15}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.4 |                 20.0 |
| Hikaru Nakamura        |      35.4 |                 18.1 |
| Levon Aronian          |      16.5 |                 15.0 |
| Leinier Dominguez      |      15.1 |                 14.0 |
| Wesley So              |      13.3 |                 11.8 |
| Anish Giri             |      11.8 |                 12.8 |
| Maxime Vachier-Lagrave |       6.7 |                 11.2 |
| Shakhriyar Mamedyarov  |       1.9 |                  8.5 |
| Sam Shankland          |       0.4 |                  6.7 |
| Nikita Vitiugov        |       0.3 |                  5.9 |
| Andrey Esipenko        |       0.2 |                  4.9 |
{: .w15}

**Draw:** Wesley So vs. Alexandr Predke
{: .d15}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.6 |                 20.0 |
| Hikaru Nakamura        |      40.3 |                 18.8 |
| Levon Aronian          |      19.8 |                 15.5 |
| Leinier Dominguez      |      12.0 |                 13.7 |
| Anish Giri             |      10.9 |                 11.5 |
| Maxime Vachier-Lagrave |       9.4 |                 11.2 |
| Wesley So              |       3.1 |                  6.9 |
| Shakhriyar Mamedyarov  |       2.6 |                  8.9 |
| Sam Shankland          |       1.1 |                  8.1 |
| Nikita Vitiugov        |       0.9 |                  7.2 |
| Alexandr Predke        |       0.3 |                  7.0 |
{: .d15}

**Black Wins:** Wesley So vs. Alexandr Predke
{: .b15}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |     100.0 |                 20.0 |
| Leinier Dominguez      |      34.0 |                 15.1 |
| Levon Aronian          |      33.3 |                 16.6 |
| Maxime Vachier-Lagrave |      12.6 |                 10.4 |
| Anish Giri             |      12.1 |                 11.9 |
| Hikaru Nakamura        |       5.4 |                 15.2 |
| Shakhriyar Mamedyarov  |       1.9 |                  7.1 |
| Alexandr Predke        |       0.7 |                 10.2 |
{: .b15}

**White Wins:** Yu Yangyi vs. Nikita Vitiugov
{: .w16}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.5 |                 20.0 |
| Hikaru Nakamura        |      42.9 |                 18.8 |
| Levon Aronian          |      25.7 |                 15.7 |
| Leinier Dominguez      |      16.6 |                 14.3 |
| Anish Giri             |       8.4 |                 12.4 |
| Wesley So              |       5.6 |                  9.8 |
| Maxime Vachier-Lagrave |       1.8 |                  9.8 |
| Sam Shankland          |       0.4 |                  7.6 |
| Alexandr Predke        |       0.2 |                  6.0 |
{: .w16}

**Draw:** Yu Yangyi vs. Nikita Vitiugov
{: .d16}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      99.1 |                 20.0 |
| Hikaru Nakamura        |      31.9 |                 17.9 |
| Leinier Dominguez      |      17.2 |                 14.2 |
| Levon Aronian          |      16.8 |                 15.1 |
| Anish Giri             |      12.0 |                 12.1 |
| Wesley So              |       9.7 |                  9.7 |
| Maxime Vachier-Lagrave |       9.7 |                 11.5 |
| Shakhriyar Mamedyarov  |       2.3 |                  8.2 |
| Sam Shankland          |       0.8 |                  6.9 |
| Nikita Vitiugov        |       0.4 |                  6.7 |
| Alexandr Predke        |       0.1 |                  5.6 |
{: .d16}

**Black Wins:** Yu Yangyi vs. Nikita Vitiugov
{: .b16}

| Name                   |   Qualify |   Expected GP Points |
|:-----------------------|----------:|---------------------:|
| Richard Rapport        |      98.8 |                 20.0 |
| Hikaru Nakamura        |      32.6 |                 17.7 |
| Levon Aronian          |      16.3 |                 15.2 |
| Anish Giri             |      15.0 |                 12.9 |
| Wesley So              |      11.9 |                  9.7 |
| Maxime Vachier-Lagrave |      11.2 |                 11.7 |
| Leinier Dominguez      |       6.9 |                 12.6 |
| Shakhriyar Mamedyarov  |       5.0 |                 10.2 |
| Nikita Vitiugov        |       1.3 |                  8.6 |
| Andrey Esipenko        |       1.1 |                  5.6 |
| Alexandr Predke        |       0.0 |                  4.4 |
| Sam Shankland          |       0.0 |                  7.6 |
{: .b16}

