"""How many past seasons to tune on, chosen without touching 2025: grade 2024 three ways.
Run:  python3 pick_window.py
Result (2026-10-23): tuned on 2023 only 2.09, on 2021-23 2.08, on 2019-23 2.06 -> the 5 seasons before.
An NFL season is about 270 games, so one season is a small sample to choose settings on."""
import statistics as st
from data import load
from model import tuned_models, run, gaps

if __name__ == "__main__":
    games = load()
    for size in (1, 3, 5):
        seasons = tuple(str(s) for s in range(2024 - size, 2024))
        m = tuned_models(games, seasons, "line")
        print(f"tuned on {seasons[0]} to {seasons[-1]}: 2024 full model {st.mean(gaps(games, run(games, **m['+ division games']), '2024')):.3f}")
