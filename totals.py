"""Over/under line-making: price each game's total points the day before, graded against the closing total.

- Each team has an offence rating (points it scores above the league average) and a defence rating
  (points it allows above average). The league average drifts as scoring changes.
- Expected home points = league average + home offence + away defence, and the same for the away team.
  The predicted total is the sum.
- After each day, ratings move toward the actual points and, as an improvement, toward the closing total.
  A starting quarterback listed out, and other starters listed out, lower a team's expected points.
"""
import statistics as st
from model import game_days


def run(games, k=0.03, carry=0.6, k_avg=0.01, k_market=0.0, qb=0.0, inj=0.0):
    off, dfn, avg, season, preds = {}, {}, 22.0, None, []
    for day in game_days(games):
        if day[0]["season"] != season:
            season = day[0]["season"]
            off = {t: r * carry for t, r in off.items()}
            dfn = {t: r * carry for t, r in dfn.items()}
        day_preds = []
        for g in day:  # price the whole day first
            h, a = g["home"], g["away"]
            ph = avg + off.get(h, 0.0) + dfn.get(a, 0.0) + qb * g["home_qb"] - inj * g["home_starters_out"]
            pa = avg + off.get(a, 0.0) + dfn.get(h, 0.0) + qb * g["away_qb"] - inj * g["away_starters_out"]
            day_preds.append((ph, pa))
        preds.extend(ph + pa for ph, pa in day_preds)
        for g, (ph, pa) in zip(day, day_preds):  # then learn from it
            h, a = g["home"], g["away"]
            eh, ea = g["home_pts"] - ph, g["away_pts"] - pa
            off[h], dfn[a] = off.get(h, 0.0) + k * eh, dfn.get(a, 0.0) + k * eh
            off[a], dfn[h] = off.get(a, 0.0) + k * ea, dfn.get(h, 0.0) + k * ea
            avg += k_avg * (eh + ea) / 2
            if k_market and g["learn_total"] is not None:
                m = (g["learn_total"] - ph - pa) / 4
                for d, t in ((off, h), (off, a), (dfn, h), (dfn, a)):
                    d[t] = d.get(t, 0.0) + k_market * m
    return preds


def gaps(games, preds, season, line="close_total"):
    seasons = {season} if isinstance(season, str) else set(season)
    return [abs(p - g[line]) for g, p in zip(games, preds) if g["season"] in seasons and g[line] is not None]


def tune(games, grid, seasons):
    return min(((st.mean(gaps(games, run(games, **p), seasons, "learn_total")), p) for p in grid), key=lambda x: x[0])


def tuned_models(games, seasons):
    _, base = tune(games, [dict(k=k, carry=c, k_avg=a) for k in (0.02, 0.03, 0.05, 0.07, 0.1)
                           for c in (0.3, 0.5, 0.7) for a in (0.002, 0.005, 0.01, 0.02)], seasons)
    _, mkt = tune(games, [dict(base, k_market=x) for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8)], seasons)
    _, qbs = tune(games, [dict(mkt, qb=x) for x in (0, 0.25, 0.5, 0.75, 1.0)], seasons)
    _, injp = tune(games, [dict(qbs, inj=x) for x in (0, 0.1, 0.2, 0.3, 0.5, 0.75)], seasons)
    return {"baseline": base, "+ past closes": mkt, "+ quarterbacks": qbs, "+ other injuries": injp}
