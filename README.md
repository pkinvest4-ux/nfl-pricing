# Pricing NFL Spreads the Day Before

Prices every NFL game with what was known by the end of the day before, and grades the price against
the pre-game closing line. The starting model was 2.10 points off the close on 2025; with the
improvements, it's **1.78**.

A companion to [nba-pricing-trial](https://github.com/pkinvest4-ux/nba-pricing-trial), built the same way.

## Start here

1. **[WRITEUP.md](WRITEUP.md):** the one-page summary.
2. **[HOW_IT_WORKS.md](HOW_IT_WORKS.md):** a walk through the code, in the order a game gets priced.
3. **[EXAMPLE_GAME.md](EXAMPLE_GAME.md):** one real game, start to finish.
4. **[DETAILS.md](DETAILS.md):** every number, season by season.
5. **[results_by_game.csv](results_by_game.csv):** every game of 2025 and 2026 so far: how each number was
   built, the close and the result. [results_summary.csv](results_summary.csv) has the season totals.

## Run it

Python 3.10 or newer, standard library only.

```bash
python3 fetch_data.py         # download everything into data/ (cached)
python3 evaluate.py           # grade 2025, the test season
python3 evaluate.py 2026      # grade this season so far
python3 walkforward.py        # each season 2016 to 2025, tuned on the 5 before it
python3 explain.py SF NO 2025-09-14   # how one game was priced, piece by piece
python3 export_results.py     # rewrite the spreadsheets
python3 pick_window.py        # how the 5-season tuning window was chosen
```

## Files

| File | Job |
|---|---|
| `data.py` | Everything known the day before a game: the closing line, rest, quarterbacks, other starters out |
| `model.py` | The spread model: price each day's games, then learn from them; choose the settings |
| `totals.py` | The over/under model |
| `evaluate.py` | Grade each step against the close, check which gains are real, win probability, totals |
| `walkforward.py` | Ten seasons, each tuned on the 5 before it |
| `pick_window.py` | How many past seasons to tune on, chosen on 2024 |
| `explain.py` | Show how one game's number was built |
| `export_results.py` | Write `results_by_game.csv` and `results_summary.csv` |
| `fetch_data.py` | Download games, injury reports, rosters, player stats, snap counts (nflverse) and closing lines (ESPN) |
| `common.py` | Web requests |

## Rules the code follows

- A day's games are priced before any of that day's results or lines are used.
- Injuries come from the final injury report, published before game day. Game-day inactives are not used.
- Every setting is chosen on seasons before the one being graded.
- 2024 on is graded against one book's pre-game close, as recorded by ESPN.
