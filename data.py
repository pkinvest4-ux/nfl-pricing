"""Everything known before an NFL game, from the files fetch_data.py downloads.

load() returns every game since 2012, in date order, each with:
  close / close_total / close_prob   the answer key: ESPN's recorded pre-game close (2024 on); None before
  learn_close / learn_total          a closing line to learn from in every season (ESPN's close, else nflverse's)
  home_rest / away_rest              days since each team's last game (the schedule is public months ahead)
  home_qb / away_qb                  the quarterback change: value of the expected starter minus the usual one
  home_starters_out / away_...       other starters on the final injury report (Out 1, Doubtful 0.75, Questionable 0.25)
"""
import csv
import json
import unicodedata
from collections import defaultdict, deque

TUNE, TEST, LIVE = "2024", "2025", "2026"   # TEST is graded once; LIVE is the season being played now


def window(season, size=5):
    """The seasons a test season is tuned on: the 5 before it. (Chosen on 2024: tuned on 2019-23 it was
    2.06 off the close, against 2.08 for the 3 seasons before and 2.09 for 1. See pick_window.py.)"""
    return tuple(str(s) for s in range(int(season) - size, int(season)))
FIRST = 2012
MOVED = {"OAK": "LV", "SD": "LAC", "STL": "LA"}  # one code per franchise
QB_GAMES, QB_PRIOR, QB_PRIOR_GAMES = 16, 2.0, 4.0   # a quarterback's value: EPA a game over his last 16 starts,
BACKUP = -6.0                                        # pulled toward 2.0 as if he had 4 more; an unknown backup is -6


def team(code):
    return MOVED.get(code, code)


def num(x):
    return float(x) if x not in ("", None, "NA") else None


def no_vig(home_ml, away_ml):
    """Home team's fair win probability from the two moneylines, with the book's margin removed."""
    if home_ml is None or away_ml is None:
        return None
    imp = lambda ml: 100 / (ml + 100) if ml > 0 else -ml / (-ml + 100)
    h, a = imp(home_ml), imp(away_ml)
    return h / (h + a)


def key_book(season):
    """The book whose close is the answer key: ESPN BET, until ESPN switched to DraftKings late in 2025."""
    return {"2024": ("ESPN BET",), "2025": ("ESPN BET", "DraftKings"), "2026": ("DraftKings",)}.get(season, ())


def load():
    rows = [g for g in csv.DictReader(open("data/games.csv")) if int(g["season"]) >= FIRST and g["result"]]
    odds = json.load(open("data/espn_odds.json"))
    games = []
    for r in rows:
        g = {"id": r["game_id"], "season": r["season"], "week": int(r["week"]), "date": r["gameday"],
             "type": r["game_type"], "home": team(r["home_team"]), "away": team(r["away_team"]),
             "margin": int(r["result"]), "total": int(r["total"]), "neutral": r["location"] == "Neutral",
             "home_pts": int(r["home_score"]), "away_pts": int(r["away_score"]),
             "home_rest": int(r["home_rest"]), "away_rest": int(r["away_rest"]), "div": r["div_game"] == "1"}
        spread, total = num(r["spread_line"]), num(r["total_line"])   # nflverse: positive = home favoured
        g["close"] = g["close_total"] = g["close_prob"] = g["book"] = None
        for b in key_book(g["season"]):
            rec = odds.get(r["espn"], {}).get(b)
            if rec and rec.get("close_spread") is not None:
                g["close"], g["book"] = rec["close_spread"], b         # home spread: -3 = home by 3
                g["close_total"] = rec.get("close_total") or rec.get("total")
                g["close_prob"] = no_vig(rec.get("close_ml_home"), rec.get("close_ml_away"))
                break
        g["learn_close"] = g["close"] if g["close"] is not None else (-spread if spread is not None else None)
        g["learn_total"] = g["close_total"] if g["close_total"] is not None else total
        g["line"] = g["learn_close"]   # graded against in seasons with no labelled close (the ten-season run)
        games.append(g)
    games.sort(key=lambda g: (g["date"], g["id"]))
    add_quarterbacks(games)
    add_starters(games)
    return games


def add_quarterbacks(games):
    """Who starts at quarterback, known the day before: last game's starter, unless the final injury
    report lists him Out or Doubtful or he is on injured reserve, in which case the team's other recent quarterback (or an unknown
    backup). Each quarterback's value is his EPA (expected points added, passing + rushing) a game.
    home_qb / away_qb = expected starter's value minus the usual starter's: zero unless he is out."""
    starters = {}   # game_id -> {team: (gsis_id, epa)}
    for s in range(FIRST, int(LIVE) + 1):
        best = {}
        for p in csv.DictReader(open(f"data/stats_{s}.csv")):
            if p["position"] != "QB":
                continue
            att = int(float(p["attempts"] or 0)) + int(float(p["carries"] or 0))
            epa = (num(p["passing_epa"]) or 0.0) + (num(p["rushing_epa"]) or 0.0)
            k = (p["game_id"], team(p["team"]))
            if att > best.get(k, (0,))[0]:
                best[k] = (att, p["player_id"], epa)
        for (gid, t), (_, pid, epa) in best.items():
            starters.setdefault(gid, {})[t] = (pid, epa)
    out = defaultdict(set)   # (season, week, team) -> players known to be out before the game:
    for s in range(FIRST, int(LIVE) + 1):  # Out or Doubtful on the final injury report, or on reserve (IR)
        for p in csv.DictReader(open(f"data/injuries_{s}.csv")):
            if p["report_status"] in ("Out", "Doubtful"):
                out[p["season"], int(p["week"]), team(p["team"])].add(p["gsis_id"])
        for p in csv.DictReader(open(f"data/rosters_{s}.csv")):
            if p["status"] == "RES" and p["position"] == "QB":   # not INA: game-day inactives are not known yet
                out[p["season"], int(p["week"]), team(p["team"])].add(p["gsis_id"])

    history = defaultdict(lambda: deque(maxlen=QB_GAMES))   # quarterback -> EPA in his recent starts
    last, recent = {}, defaultdict(lambda: deque(maxlen=3))  # team -> last starter; team -> recent starters

    def value(pid):
        h = history.get(pid, ())
        return (sum(h) + QB_PRIOR * QB_PRIOR_GAMES) / (len(h) + QB_PRIOR_GAMES) if pid else BACKUP

    by_date = defaultdict(list)
    for g in games:
        by_date[g["date"]].append(g)
    for day in sorted(by_date):
        for g in by_date[day]:
            for side in ("home", "away"):
                t = g[side]
                usual = last.get(t)
                listed = out.get((g["season"], g["week"], t), set())
                expected = usual
                if usual in listed:
                    others = [q for q in reversed(recent[t]) if q != usual and q not in listed]
                    expected = others[0] if others else None
                g[side + "_qb"] = (value(expected) - value(usual)) if usual else 0.0
                g[side + "_qb_out"] = usual in listed if usual else False
        for g in by_date[day]:  # only now is the day's box score known
            for side in ("home", "away"):
                st = starters.get(g["id"], {}).get(g[side])
                if st:
                    pid, epa = st
                    history[pid].append(epa)
                    last[g[side]] = pid
                    if pid not in recent[g[side]]:
                        recent[g[side]].append(pid)


STATUS = {"Out": 1.0, "Doubtful": 0.75, "Questionable": 0.25}
STARTER_SHARE, STARTER_GAMES = 0.6, 4   # a starter: 60%+ of offensive or defensive snaps over the team's last 4 games


def norm(name):
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    name = " ".join(w for w in name.replace(".", "").replace("'", "").split() if w not in ("jr", "sr", "ii", "iii", "iv"))
    return name


def add_starters(games):
    """How many regular starters (not quarterbacks) each team has on the final injury report. A starter
    played 60%+ of the offensive or defensive snaps, on average, in the team's last 4 games."""
    snaps = defaultdict(dict)   # game_id -> {(team, name): share}
    for s in range(2013, int(LIVE) + 1):
        for p in csv.DictReader(open(f"data/snaps_{s}.csv")):
            if p["position"] == "QB":
                continue
            share = max(float(p["offense_pct"] or 0), float(p["defense_pct"] or 0))
            snaps[p["game_id"]][team(p["team"]), norm(p["player"])] = share
    listed = defaultdict(dict)  # (season, week, team) -> {name: weight}
    for s in range(FIRST, int(LIVE) + 1):
        for p in csv.DictReader(open(f"data/injuries_{s}.csv")):
            w = STATUS.get(p["report_status"])
            if w and p["position"] != "QB":
                listed[p["season"], int(p["week"]), team(p["team"])][norm(p["full_name"])] = w
    recent = defaultdict(lambda: deque(maxlen=STARTER_GAMES))   # team -> its last 4 game ids
    by_date = defaultdict(list)
    for g in games:
        by_date[g["date"]].append(g)
    for day in sorted(by_date):
        for g in by_date[day]:
            for side in ("home", "away"):
                t, n = g[side], 0.0
                ids = recent[t]
                for name, w in listed.get((g["season"], g["week"], t), {}).items():
                    shares = [snaps[i].get((t, name), 0.0) for i in ids]
                    if ids and sum(shares) / len(ids) >= STARTER_SHARE:
                        n += w
                g[side + "_starters_out"] = n
        for g in by_date[day]:
            for side in ("home", "away"):
                if g["id"] in snaps:
                    recent[g[side]].append(g["id"])
