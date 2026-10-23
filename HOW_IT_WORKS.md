# How it works

A walk through the code in the order a game gets priced. Each section names the file and function.

## 1. The idea

The goal is to price a game the day before, and to get as close as possible to where the market finally
settles: the **closing line**. By kickoff it has every bet and every piece of news in it, so it is the
best estimate of the game there is. The score that matters: **average points between my number and the
closing spread**.

## 2. The data (`fetch_data.py`)

| File | What it is | Why |
|---|---|---|
| `games.csv` | Every game, score, rest days and line (nflverse) | Results to learn from |
| `injuries_<season>.csv` | Each week's final injury report | Who is out |
| `rosters_<season>.csv` | Each week's roster status | Quarterbacks on injured reserve |
| `stats_<season>.csv` | Every player's stats in every game | Quarterback value (EPA per game) |
| `snaps_<season>.csv` | Every player's share of snaps | Who the starters are |
| `espn_odds.json` | Each book's pre-game close, 2024 on (ESPN) | The answer key |

Everything is cached in `data/`, so it only downloads once.

## 3. What is known the day before (`data.py`)

`load()` reads the files and adds these to every game:

- **The answer key.** ESPN BET's close, then DraftKings' once ESPN switched partners late in 2025.
  `no_vig` turns the closing moneyline into a fair win probability.
- **Rest.** Days since each team's last game. The schedule is public months ahead.
- **`add_quarterbacks`.** Last game's starter is the expected starter, unless the final injury report
  lists him Out or Doubtful or he is on injured reserve; then it's the team's other recent quarterback,
  or an unknown backup (valued at -6). A quarterback's value is his EPA per game over his last 16 starts,
  pulled toward average if he has few. Two numbers come out: the drop from the usual starter, and the
  expected starter against the team's usual quarterback over its last 8 games.
- **`add_starters`.** How many other starters each team has on the final injury report (Out 1, Doubtful
  0.75, Questionable 0.25). A starter played 60%+ of the offensive or defensive snaps in the team's last
  4 games.

## 4. Pricing a day, then learning (`model.py`, `run`)

**Step 1, price the day.** The predicted home margin is the sum of these parts:

| Part | What it is | Final setting |
|---|---|---|
| Team ratings | Home rating minus away rating, in points | learned |
| Home field | Same for every home team | 1.5 points |
| Rest | Points for a week more rest than the opponent | 1.0 |
| Quarterbacks | The drop when a starter is out, and the starter against the usual one | 0.25 and 0.2 |
| Other injuries | Points per other starter listed out | 0.3 |

Then the margin shrinks by 5% in division games.

**Step 2, learn from the day.** Only after every game on the day is priced:
- Each team's rating moves 7% of the way toward the actual result (`k`).
- And 20% of the way toward the closing line (`k_market`), the biggest single improvement.

**At the start of each season,** team ratings keep 60% of their value (`carry`).

## 5. Choosing the settings (`model.py`, `tuned_models`)

The model is built one step at a time. For each step, every setting in a small grid is tried on the 5
seasons before the one being graded, and the one closest to the line is kept. Then the next step is added.
`pick_window.py` shows how 5 seasons was chosen (on 2024, before 2025 was graded).

## 6. Grading (`evaluate.py`)

- **Points off the close** for every step.
- **Is a gain real?** The games are resampled 10,000 times and the gain recomputed each time. If the
  middle 95% is entirely above zero, the gain is real.
- **Against the real result,** win probability (graded with log loss), and the totals model (`totals.py`).

## 7. Ten seasons (`walkforward.py`)

The same process for each season from 2016 to 2025, each tuned on the 5 before it. Seasons before 2024
are graded against nflverse's line, because ESPN has no labelled close for them.

## 8. One game, start to finish (`explain.py`)

`python3 explain.py SF NO 2025-09-14` prints each part for 49ers at Saints. The output is written up in
[EXAMPLE_GAME.md](EXAMPLE_GAME.md).

## 9. The spreadsheets (`export_results.py`)

`results_by_game.csv` has one row per game of 2025 and 2026 so far: each part of the number, the model, the
close, the result, and the same for the total. `results_summary.csv` has one row per season.
