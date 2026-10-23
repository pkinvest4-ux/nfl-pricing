# Pricing NFL Spreads the Day Before

**Patrick Kooy Velazquez** · A second sport, built the same way as the NBA trial · October 2026

**The result:** my starting model was **2.10 points** off the pre-game close on the 2025 season. With the
improvements, it's **1.78**.

---

## 1. The model

I price each game with what's known by the end of the day before, walking through the schedule one day
at a time: price the day's games, then learn from their results and closing lines.

**Starting model.** Every team starts at 0. After each game, both teams' ratings move 7% of the way toward
the actual result. The predicted margin is the rating gap plus 1.5 points of home field. Each new season,
teams keep 60% of their rating. That's the 2.10.

**Improvements, one at a time:**

1. **Learn from past closing lines.** Ratings also move 20% of the way toward each game's closing line.
   The market knows things a box score doesn't. (1.91)
2. **Rest.** A team with a week more rest than its opponent (a bye, or the other team coming off a
   Thursday game) gets 1 point. (1.93)
3. **Quarterbacks.** A quarterback's value is his expected points added (EPA) per game. If last game's
   starter is out on the final injury report or on injured reserve, his backup's value is used instead.
   When a new starter has taken over, he's also compared with the team's usual quarterback, since team
   ratings take weeks to catch up. (1.82)
4. **Other injuries.** Each other starter listed out costs his team 0.3 points. A starter played 60%+ of
   the snaps in the team's last four games. (1.79)
5. **Division games.** Rivals play closer games, so the margin shrinks by 5%. (1.78)

## 2. The data

- **Closing lines:** ESPN's recorded pre-game closes: ESPN BET for 2024 and most of 2025, DraftKings for
  the end of 2025. Older seasons use nflverse's line.
- **Everything else:** nflverse, a free public NFL dataset: games and rest days, the weekly final injury
  report, weekly rosters (injured reserve), player stats (quarterback value) and snap counts (who starts).

## 3. How I tested it

An NFL season is only about 270 games, so I choose settings on the 5 seasons before the one being graded.
I picked that window by grading 2024 first (5 seasons beat 3 or 1). To make sure one season wasn't luck, I
repeated the whole process for each of the last ten seasons. A gain counts as real if it holds in 95% of
10,000 resamples of the games.

## 4. Results

| Step | 2025 off the close | Gain on 2025 (95% range) | Ten seasons together (95% range) |
|---|---|---|---|
| Starting model | 2.10 | | |
| + learn from past closing lines | 1.91 | +0.19 (0.04 to 0.33) | +0.35 (0.30 to 0.40), better 10 of 10 |
| + rest | 1.93 | -0.02 (-0.06 to 0.02) | +0.03 (0.01 to 0.04), better 6 of 10 |
| + quarterbacks | 1.82 | +0.12 (0.03 to 0.20) | +0.05 (0.03 to 0.07), better 9 of 10 |
| + other injuries | 1.79 | +0.03 (-0.01 to 0.07) | +0.02 (0.01 to 0.04), better 8 of 10 |
| + division games | **1.78** | +0.01 (-0.01 to 0.03) | +0.01 (0.01 to 0.02), better 9 of 10 |

- Learning from past closing lines is the biggest improvement again, as it was in the NBA. Quarterbacks
  are second, which is what you'd expect in football.
- One NFL season is too small to prove the smaller steps on its own. Across ten seasons (2,760 games),
  all five are real.
- For scale, a book's own opening line ends up about 1.3 points from its close.
- Against the final scores, the close still beats me: it's 9.64 points off on average, and I'm 10.01.

## 5. Second numbers

- **Win probability:** 5.7 percentage points from the no-vig closing price, with a log loss of 0.629
  against the close's 0.609.
- **Totals:** 2.40 down to **1.89 points** off the closing total, from learning past closing totals.

## 6. Order of work

I graded 2025 twice: 1.87 with the first four steps (code frozen in git, `2def6b4`), then 1.78 after adding
the quarterback-level and division steps, which I chose on 2016 to 2024 only (`c1f797f`).

The full numbers are in [DETAILS.md](DETAILS.md), and every game is in [results_by_game.csv](results_by_game.csv).
