# Full notes

Every number behind [WRITEUP.md](WRITEUP.md). For how the code works, see [HOW_IT_WORKS.md](HOW_IT_WORKS.md).
All figures are points between the model's number and the line, averaged over games, unless stated.

## Data

- **Answer key.** ESPN's recorded pre-game close: ESPN BET for 2024 (284 games) and 193 games of 2025,
  DraftKings for the last 92 games of 2025 and for 2026. ESPN keeps in-game odds under separate "Live Odds"
  entries, so these are pre-game numbers. Seasons before 2024 use nflverse's spread line.
- **nflverse** (github.com/nflverse): games, scores and rest days; each week's final injury report (2012
  on); weekly rosters, used only for injured reserve, never for game-day inactives; player stats, for each
  quarterback's expected points added (EPA) per game; snap counts (2013 on), to tell who starts.
- Regular season and playoffs, 2012 on.

## Settings

Chosen on the 5 seasons before the graded one (2020 to 2024 for 2025):

| Setting | Value | Meaning |
|---|---|---|
| `k` | 0.07 | team ratings move 7% of the way toward each result |
| `hca` | 1.5 | home field, points |
| `carry` | 0.6 | share of a team rating kept into a new season |
| `k_market` | 0.2 | ratings move 20% of the way toward each closing line |
| `rest` | 1.0 | points for a full week more rest than the opponent |
| `qb` | 0.25 | weight on the drop when last game's starter is out |
| `qb_level` | 0.2 | weight on the expected starter against the team's usual quarterback (last 8 games) |
| `inj` | 0.3 | points per other starter listed out |
| `div` | 0.05 | share the margin shrinks in division games |

A quarterback's value is his EPA per game over his last 16 starts, pulled toward 2.0 as if he had 4 more;
an unknown backup is -6.

## Spreads, 2025 (test season, 285 games)

| Step | Off the close | Gain (95% range) |
|---|---|---|
| Starting model | 2.10 | |
| + learn from past closing lines | 1.91 | +0.19 (0.04 to 0.33) |
| + rest | 1.93 | -0.02 (-0.06 to 0.02) |
| + quarterbacks | 1.82 | +0.12 (0.03 to 0.20) |
| + other injuries | 1.79 | +0.03 (-0.01 to 0.07) |
| + division games | **1.78** | +0.01 (-0.01 to 0.03) |

Within 1 point of the close in 42% of games, within 2 in 70%, 4+ off in 8%. A book's opening line ends up
1.34 points from its close on average in 2025 (1.20 in 2024). Against the actual margin: model 10.01, close
9.64 (close better by 0.37, 0.11 to 0.63). Average lean toward the home team versus the close: -0.15.

## Win probability, 2025

Actual margins land around the prediction with a spread of 13.0 points (measured on the tuning seasons).
5.7 percentage points from the no-vig closing price; log loss 0.629 against the close's 0.609 (close better
by 0.020, 0.002 to 0.037).

## Totals, 2025

Offence and defence ratings around a drifting league average, learning from past closing totals.

| Step | Off the closing total | Gain (95% range) |
|---|---|---|
| Starting model | 2.40 | |
| + learn from past closing totals | 1.89 | +0.51 (0.34 to 0.68) |
| + quarterbacks | 1.90 | -0.00 (-0.08 to 0.08) |
| + other injuries | **1.89** | +0.00 (-0.01 to 0.02) |

## Ten seasons, each tuned on the 5 before it (`walkforward.py`)

```
season         baseline     past closes            rest    quarterbacks  other injuries  division games
2016               1.91            1.71            1.67            1.69            1.64            1.63
2017               2.38            2.00            1.92            1.86            1.81            1.78
2018               2.22            1.76            1.76            1.73            1.73            1.73
2019               2.33            1.99            1.98            1.97            1.94            1.94
2020               2.58            2.42            2.38            2.33            2.31            2.28
2021               2.63            2.04            2.00            1.91            1.92            1.91
2022               2.48            2.03            2.04            2.03            1.99            1.98
2023               2.17            1.98            1.98            1.98            1.97            1.95
2024               2.78            2.28            2.21            2.09            2.05            2.04
2025               2.10            1.91            1.93            1.82            1.79            1.78
```

All ten seasons together (2,760 games): starting model 2.36, full model 1.90.

| Step | Gain (95% range) | Better in |
|---|---|---|
| + learn from past closing lines | +0.35 (0.30 to 0.40) | 10 of 10 seasons |
| + rest | +0.03 (0.01 to 0.04) | 6 of 10 |
| + quarterbacks | +0.05 (0.03 to 0.07) | 9 of 10 |
| + other injuries | +0.02 (0.01 to 0.04) | 8 of 10 |
| + division games | +0.01 (0.01 to 0.02) | 9 of 10 |

Before 2024 the line is nflverse's, not a labelled close, so compare steps within a season rather than
levels across seasons.

## 2026 so far (94 games, weeks 1 to 7)

Tuned on 2021 to 2025: starting model 2.43, full model 2.02 off the DraftKings close.

## Order of work

1. The first four steps were built and checked on 2022 to 2024. The tuning window was chosen on 2024
   (`pick_window.py`: tuned on 2023 only 2.09, on 2021 to 2023 2.08, on 2019 to 2023 2.06).
2. Code frozen (`2def6b4`), 2025 graded once: 2.10, 1.91, 1.93, 1.92, 1.87.
3. Three more ideas were tested on 2016 to 2024 only, each season tuned on the 5 before it. Kept: the
   quarterback level (better in 8 of 9 seasons) and division games (better in 8 of 9, worse in none).
   Dropped: learning from each game's EPA instead of the score (worse in 6 of 9), and pulling numbers
   toward 3 and 7 (+0.006, too small to keep).
4. Code frozen (`c1f797f`), 2025 graded a second time: 1.78.
5. Two more ideas were tested on 2016 to 2024 only and not kept, so 2025 was not graded again:
   - **Position groups.** Starters out counted separately for the offensive line, defensive line,
     linebackers, secondary, receivers and running backs, each with its own weight: worse on average
     (-0.003; better in 6 of 9 seasons, worse in 3). Split only into offence and defence: +0.000. With about
     270 games a season, separate weights mostly fit noise; one weight for every starter does as well.
   - **Player ratings,** as in the NBA model: every player rated from the closing lines of the games he
     played, by snap share, and the two expected lineups compared: +0.001, better in 3 of 9 seasons. The
     market already prices individual players better than this.
