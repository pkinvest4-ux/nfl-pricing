"""The spread model: price each week's games, then learn from them.

Predicted home margin =
      home team rating - away team rating        (learned from results and past closing lines)
    + home-court advantage
    + rest                                        (rest x the gap in days since each team's last game, capped at a week)
    + quarterback change                          (qb x the drop when a starter is listed out)
    + other injuries                              (inj x the gap in other starters listed out)

After a day's games are played, team ratings move toward the actual margin (k) and toward the closing
line (k_market). At the start of each season every rating shrinks toward average (carry).
A positive margin means the home team is favoured. Every rating is in points.
"""
import statistics as st
from collections import defaultdict
from data import TUNE


def game_days(games):
    days = defaultdict(list)
    for g in games:
        days[g["date"]].append(g)
    return [days[d] for d in sorted(days)]


# The settings ("dials"). Defaults are starting values; the final ones are chosen in tuned_models():
#   k        how far a team rating moves toward each result (0.05 = 5% of the miss)
#   hca      home-court advantage, in points
#   carry    share of a team rating kept from one season to the next
#   k_market how far a team rating moves toward each closing line
#   rest     points for a full week more rest than the opponent
#   qb       weight on the quarterback change (1.0 = one point per point of EPA a game)
#   inj      points per other starter listed out
def run(games, k=0.05, hca=2.0, carry=0.6, k_market=0.0, rest=0.0, qb=0.0, inj=0.0, trace=None):
    """Walk through every season one day at a time. Returns each game's predicted home margin."""
    team, season, preds = {}, None, []
    for day in game_days(games):
        if day[0]["season"] != season:  # a new season: ratings shrink toward average
            season = day[0]["season"]
            team = {t: r * carry for t, r in team.items()}

        # 1. Price every game on the day, using only what was known before it.
        day_preds = []
        for g in day:
            parts = {
                # gap between the two team ratings
                "team": team.get(g["home"], 0.0) - team.get(g["away"], 0.0),
                # home field, unless the game is at a neutral site
                "home_court": 0 if g["neutral"] else hca,
                # extra rest (bye weeks, Thursday games), capped at a week either way
                "rest": rest * max(-7, min(7, g["home_rest"] - g["away_rest"])) / 7,
                # a starting quarterback listed Out or Doubtful on the final injury report
                "qb": qb * (g["home_qb"] - g["away_qb"]),
                # other starters listed on the final injury report
                "injuries": inj * (g["away_starters_out"] - g["home_starters_out"]),
            }
            p = sum(parts.values())
            day_preds.append(p)
            if trace is not None:
                trace[g["id"]] = dict(parts, total=p)
        preds.extend(day_preds)

        # 2. Only now learn from the day's results and closing lines.
        for g, p in zip(day, day_preds):
            miss_result = g["margin"] - p
            team[g["home"]] = team.get(g["home"], 0.0) + k * miss_result
            team[g["away"]] = team.get(g["away"], 0.0) - k * miss_result
            if k_market and g["learn_close"] is not None:
                miss_close = -g["learn_close"] - p  # the close is the home spread, so -close is the market's margin
                team[g["home"]] += k_market * miss_close
                team[g["away"]] -= k_market * miss_close
    return preds


# ---------- choosing the settings ----------

def gaps(games, preds, season, line="close", only=None):
    """Points between our number and the line, for every graded game in a season (or list of seasons)."""
    seasons = {season} if isinstance(season, str) else set(season)
    return [abs(p + g[line]) for g, p in zip(games, preds)
            if g["season"] in seasons and g[line] is not None and (only is None or only(g))]


def tune(games, grid, season=None, line="close"):
    season = season or TUNE
    return min(((st.mean(gaps(games, run(games, **p), season, line)), p) for p in grid), key=lambda x: x[0])


def tuned_models(games, season=None, line="close"):
    """Build the model one step at a time, choosing each step's settings on `season` (default 2024)."""
    grid = [dict(k=k, hca=h, carry=c) for k in (0.02, 0.03, 0.05, 0.07, 0.1, 0.13)
            for h in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0) for c in (0.3, 0.45, 0.6, 0.75, 0.9)]
    _, base = tune(games, grid, season, line)
    _, closes = tune(games, [dict(base, k_market=m, k=k) for m in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8)
                             for k in (0.0, 0.01, 0.02, base["k"])], season, line)
    _, rested = tune(games, [dict(closes, rest=x) for x in (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)], season, line)
    _, qbs = tune(games, [dict(rested, qb=x) for x in (0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5)], season, line)
    _, injured = tune(games, [dict(qbs, inj=x) for x in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75)], season, line)
    return {"baseline": base, "+ past closes": closes, "+ rest": rested, "+ quarterbacks": qbs,
            "+ other injuries": injured}
