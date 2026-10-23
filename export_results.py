"""Write results_by_game.csv: every game of 2025 (test) and 2026 (this season so far), each graded with
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
    spread = run(games, **tuned_models(games, window(season), "line")["+ other injuries"], trace=trace)
    total = totals.run(games, **totals.tuned_models(games, window(season))["+ other injuries"])
    for g, p, t in zip(games, spread, total):
        if g["season"] != season or g["close"] is None:
            continue
        parts, close = trace[g["id"]], -g["close"]
        rows.append({
            "season": season, "week": g["week"], "date": g["date"], "away": g["away"], "home": g["home"],
            "book": g["book"], "team ratings": parts["team"], "home field": parts["home_court"],
            "rest": parts["rest"], "quarterbacks": parts["qb"], "other injuries": parts["injuries"],
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
