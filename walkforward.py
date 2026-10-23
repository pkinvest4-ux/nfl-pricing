"""Ten seasons, each tuned on the 5 before it and graded once. Run:  python3 walkforward.py
Seasons before 2024 have no labelled close in ESPN's data, so they are graded against nflverse's line."""
import statistics as st
from multiprocessing import Pool
from data import load, window
from model import tuned_models, gaps, run
from evaluate import bootstrap

SEASONS = [str(s) for s in range(2016, 2026)]


def one(target):
    games = load()
    line = "close" if target >= "2024" else "line"
    models = tuned_models(games, window(target), "line")
    g = {n: gaps(games, run(games, **p), target, line) for n, p in models.items()}
    names = list(models)
    return target, {n: st.mean(v) for n, v in g.items()}, [(b, *bootstrap(g[a], g[b], n=4000)) for a, b in zip(names, names[1:])], g


if __name__ == "__main__":
    with Pool(8) as pool:
        results = pool.map(one, SEASONS)
    names = list(results[0][1])
    print(f"{'season':7}" + "".join(f"{n.replace('+ ', '')[:14]:>16}" for n in names))
    for target, means, _, _ in results:
        print(f"{target:7}" + "".join(f"{means[n]:16.2f}" for n in names))
    print("\nreal gains (95% range above zero):")
    for target, _, steps, _ in results:
        print(f"  {target}: " + "  ".join(f"{b.replace('+ ', '')} {m:+.2f}{'*' if lo > 0 else ''}" for b, m, lo, hi in steps))
    print("\nall ten seasons together (each game graded with settings chosen on the 5 seasons before it):")
    for a, b in zip(names, names[1:]):
        m, lo, hi = bootstrap([x for r in results for x in r[3][a]], [x for r in results for x in r[3][b]])
        pos = sum(r[1][b] < r[1][a] for r in results)
        print(f"  {b}: {m:+.3f} points, 95% range {lo:+.3f} to {hi:+.3f}, better in {pos} of 10 seasons")
    print(f"  full model: {st.mean(x for r in results for x in r[3][names[-1]]):.2f} off the line, starting model "
          f"{st.mean(x for r in results for x in r[3][names[0]]):.2f} ({sum(len(r[3][names[0]]) for r in results)} games)")
