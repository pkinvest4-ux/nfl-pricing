"""Grade the model. Run:  python3 evaluate.py           (2025, the test season)
                        python3 evaluate.py 2026      (this season so far)

Every setting is chosen on the 5 seasons before the graded one, then that season is graded once against
ESPN's recorded pre-game close: each step's average points off the close, and whether each step's gain
is real (it still shows up in 95% of 10,000 resamples of the games). Then win probability and totals.
"""
import math
import random
import statistics as st
import sys
from data import load, window, TEST
from model import run, gaps, tuned_models
import totals


def bootstrap(a, b, n=10000, seed=7):
    """Average of (a - b) over games, with a 95% range from resampling the games."""
    rnd, d = random.Random(seed), [x - y for x, y in zip(a, b)]
    means = sorted(st.mean(rnd.choices(d, k=len(d))) for _ in range(n))
    return st.mean(d), means[int(0.025 * n)], means[int(0.975 * n)]


def steps(table, label):
    names = list(table)
    for n in names:
        print(f"  {n:18} {st.mean(table[n]):.2f}")
    for a, b in zip(names, names[1:]):
        m, lo, hi = bootstrap(table[a], table[b])
        verdict = "real" if lo > 0 else ("worse" if hi < 0 else "could be noise")
        print(f"  {b} vs {a}: {m:+.2f} points, 95% range {lo:+.2f} to {hi:+.2f} ({verdict})")


def main(season):
    games = load()
    tuned_on = window(season)
    books = sorted({g["book"] for g in games if g["season"] == season and g["book"]})
    print(f"{season}: settings chosen on {tuned_on[0]} to {tuned_on[-1]}, graded against the {' / '.join(books)} close")

    models = tuned_models(games, tuned_on, "line")
    for n, p in models.items():
        print(f"  {n:18} {p}")
    preds = {n: run(games, **p) for n, p in models.items()}
    print(f"\nSpreads ({len(gaps(games, preds['baseline'], season))} games): average points off the close")
    steps({n: gaps(games, pr, season) for n, pr in preds.items()}, "spread")

    best = preds[list(models)[-1]]
    rows = [(abs(g["margin"] - p), abs(g["margin"] + g["close"]), p + g["close"]) for g, p in zip(games, best)
            if g["season"] == season and g["close"] is not None]
    m, lo, hi = bootstrap([r[0] for r in rows], [r[1] for r in rows])
    print(f"  vs the real final margin: model misses by {st.mean(r[0] for r in rows):.2f}, the close by "
          f"{st.mean(r[1] for r in rows):.2f} (close better by {m:.2f}, {lo:.2f} to {hi:.2f})")
    print(f"  lean toward the home team vs the close: {st.mean(r[2] for r in rows):+.2f}")

    sigma = st.pstdev([g["margin"] - p for g, p in zip(games, best) if g["season"] in tuned_on])
    wp = [(0.5 * (1 + math.erf(p / (sigma * math.sqrt(2)))), g["close_prob"], g["margin"] > 0)
          for g, p in zip(games, best) if g["season"] == season and g["close_prob"] is not None and g["margin"] != 0]
    ll = lambda p, won: -math.log(min(max(p if won else 1 - p, 1e-6), 1))
    ours, book = [ll(p, w) for p, _, w in wp], [ll(b, w) for _, b, w in wp]
    m, lo, hi = bootstrap(ours, book)
    print(f"\nWin probability ({len(wp)} games, bell-curve width {sigma:.1f} points)")
    print(f"  average gap to the no-vig close: {st.mean(abs(p - b) for p, b, _ in wp) * 100:.1f} points")
    print(f"  log loss: model {st.mean(ours):.4f}, closing price {st.mean(book):.4f}, coin flip {math.log(2):.4f}"
          f" (close better by {m:.4f}, {lo:.4f} to {hi:.4f})")

    tm = totals.tuned_models(games, tuned_on)
    tp = {n: totals.run(games, **p) for n, p in tm.items()}
    print(f"\nTotals ({len(totals.gaps(games, tp['baseline'], season))} games): average points off the closing total")
    for n, p in tm.items():
        print(f"  {n:18} {p}")
    steps({n: totals.gaps(games, pr, season) for n, pr in tp.items()}, "total")
    return games, models, preds


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else TEST)
