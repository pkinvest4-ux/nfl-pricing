"""Write results_by_game.csv and results_summary.csv: every game of 2025 (test) and 2026 (this season so far), each graded with
settings chosen on the 5 seasons before it. Run:  python3 export_results.py
Positive numbers mean the home team is favoured, or wins by that much."""
import csv
from data import load, window
from model import run, tuned_models
import totals

games = load()
rows = []
for season in ("2025", "2026"):
    trace = {}
    spread = run(games, **tuned_models(games, window(season), "line")["+ division games"], trace=trace)
    total = totals.run(games, **totals.tuned_models(games, window(season))["+ other injuries"])
    for g, p, t in zip(games, spread, total):
        if g["season"] != season or g["close"] is None:
            continue
        parts, close = trace[g["id"]], -g["close"]
        rows.append({
            "season": season, "week": g["week"], "date": g["date"], "away": g["away"], "home": g["home"],
            "book": g["book"], "team ratings": parts["team"], "home field": parts["home_court"],
            "rest": parts["rest"], "quarterbacks": parts["qb"] + parts["qb_level"], "other injuries": parts["injuries"],
            "division game": "yes" if g["div"] else "no",
            "model: home by": p, "close: home by": close, "result: home by": g["margin"],
            "points off the close": abs(p - close),
            "closer to result": "model" if abs(g["margin"] - p) < abs(g["margin"] - close) else
                                "close" if abs(g["margin"] - p) > abs(g["margin"] - close) else "tie",
            "model total": t, "close total": g["close_total"], "actual total": g["total"],
            "total points off the close": abs(t - g["close_total"]) if g["close_total"] is not None else None,
        })
with open("results_by_game.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows({k: round(v, 1) if isinstance(v, float) else v for k, v in r.items()} for r in rows)
print(f"wrote results_by_game.csv ({len(rows)} games)")

import statistics as st
with open("results_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["season", "games", "spread: avg points off the close", "within 1 point", "within 2 points",
                "4+ points off", "model closer to result", "total: avg points off the close"])
    for season in ("2025", "2026"):
        s = [r for r in rows if r["season"] == season]
        off = [r["points off the close"] for r in s]
        tot = [r["total points off the close"] for r in s if r["total points off the close"] is not None]
        pct = lambda xs: f"{100 * sum(xs) / len(xs):.0f}%"
        w.writerow([season + (" (test)" if season == "2025" else " (so far)"), len(s), f"{st.mean(off):.2f}",
                    pct([x <= 1 for x in off]), pct([x <= 2 for x in off]), pct([x >= 4 for x in off]),
                    pct([r["closer to result"] == "model" for r in s]), f"{st.mean(tot):.2f}"])
print("wrote results_summary.csv")
