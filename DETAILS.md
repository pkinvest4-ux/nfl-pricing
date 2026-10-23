# Full notes

Every number behind [WRITEUP.md](WRITEUP.md). All figures are points between the model's number and the
line, averaged over games, unless stated.

## Data

- **Answer key.** ESPN's recorded pre-game close: ESPN BET for 2024 (284 games) and 193 games of 2025,
  DraftKings for the last 92 games of 2025 and all of 2026. ESPN keeps in-game odds under separate "Live
  Odds" entries, so these are pre-game numbers. Seasons before 2024 use nflverse's spread line.
- **nflverse** (github.com/nflverse): games, scores and rest days; each week's final injury report (2012
  on); weekly rosters, used only for injured reserve, never for game-day inactives; player stats, for each
  quarterback's expected points added (EPA) per game; snap counts (2013 on), to tell who starts.
- Regular season and playoffs, 2012 to 2026 week 7.

## Settings

Chosen on the 5 seasons before the graded one (2020 to 2024 for 2025):

| Setting | Value | Meaning |
|---|---|---|
| `k` | 0.07 | team ratings move 7% of the way toward each result |
| `hca` | 1.5 | home field, points |
| `carry` | 0.6 | share of a team rating kept into a new season |
| `k_market` | 0.2 | ratings move 20% of the way toward each closing line |
| `rest` | 1.0 | points for a full week more rest than the opponent |
| `qb` | 0.5 | share of the quarterback drop that counts |
| `inj` | 0.3 | points per other starter listed out (0.4 when tuned on 2021 to 2025, for 2026) |

A quarterback's value is his EPA per game over his last 16 starts, pulled toward 2.0 as if he had 4 more
starts; an unknown backup is -6. The drop counts only when last game's starter is Out or Doubtful on the
final injury report or on injured reserve.

## Spreads, 2025 (test season, 285 games)

| Step | Off the close | Gain (95% range) |
|---|---|---|
| Starting model | 2.10 | |
| + learn from past closing lines | 1.91 | +0.19 (0.04 to 0.33) |
| + rest | 1.93 | -0.02 (-0.06 to 0.02) |
| + quarterbacks | 1.92 | +0.02 (-0.06 to 0.10) |
| + other injuries | **1.87** | +0.04 (0.00 to 0.09) |

Within 1 point of the close in 41% of games, within 2 in 65%. Against the actual margin: model 10.06, close
9.64 (close better by 0.41, 0.15 to 0.68). Average lean toward the home team versus the close: -0.13.

## 2026 so far (94 games, weeks 1 to 7)

| Step | Off the close | Gain (95% range) |
|---|---|---|
| Starting model | 2.43 | |
| + learn from past closing lines | 2.26 | +0.17 (-0.07 to 0.41) |
| + rest | 2.23 | +0.03 (-0.02 to 0.08) |
| + quarterbacks | 2.12 | +0.11 (0.00 to 0.23) |
| + other injuries | **2.08** | +0.05 (-0.03 to 0.12) |

Against the actual margin: model 9.38, close 9.24.

## Win probability

Actual margins land around the prediction with a spread of 13.0 points (measured on the tuning seasons).
2025: 5.8 percentage points from the no-vig closing price; log loss 0.631 against the close's 0.609 (close
better by 0.022, 0.004 to 0.040). 2026 so far: 6.5 points; log loss 0.657 against 0.660.

## Totals

Offence and defence ratings around a drifting league average, learning from past closing totals; a
quarterback drop and other starters out lower a team's expected points.

| Step | 2025 | 2026 so far |
|---|---|---|
| Starting model | 2.40 | 2.57 |
| + learn from past closing totals | 1.89 | 2.03 |
| + quarterbacks | 1.90 | 1.99 |
| + other injuries | **1.89** | **1.96** |

Learning from past closing totals is real in both seasons (2025: +0.51, 0.34 to 0.68). The other two steps
are noise on totals.

## Ten seasons, each tuned on the 5 before it (`walkforward.py`)

```
season         baseline     past closes            rest    quarterbacks  other injuries
2016               1.91            1.71            1.67            1.65            1.61
2017               2.38            2.00            1.92            1.92            1.88
2018               2.22            1.76            1.76            1.74            1.73
2019               2.33            1.99            1.98            1.98            1.95
2020               2.58            2.42            2.38            2.36            2.33
2021               2.63            2.04            2.00            1.96            1.95
2022               2.48            2.03            2.04            2.03            2.00
2023               2.17            1.98            1.98            1.95            1.94
2024               2.78            2.28            2.21            2.13            2.06
2025               2.10            1.91            1.93            1.92            1.87
```

All ten seasons together (2,760 games): starting model 2.36, full model 1.93.

| Step | Gain (95% range) | Better in |
|---|---|---|
| + learn from past closing lines | +0.35 (0.30 to 0.40) | 10 of 10 seasons |
| + rest | +0.03 (0.01 to 0.04) | 6 of 10 |
| + quarterbacks | +0.02 (0.01 to 0.04) | 8 of 10 |
| + other injuries | +0.03 (0.02 to 0.04) | 10 of 10 |

Before 2024 the line is nflverse's, not a labelled close, so compare steps within a season rather than
levels across seasons.

## Order of work

The model was built and checked on 2022 to 2024 only. The tuning window was chosen on 2024
(`pick_window.py`: tuned on 2023 only 2.09, on 2021 to 2023 2.08, on 2019 to 2023 2.06). The code was then
frozen in git (commit `2def6b4`) and 2025 was graded once. 2026 and the ten-season run came after, with no
changes to the model.
