"""Download everything the model uses into data/ (cached; delete a file to download it again).

  games.csv               every game since 1999 with score, rest days and lines (nflverse)
  injuries_<season>.csv   each week's final injury report, 2012 on (nflverse)
  stats_<season>.csv      every player's stats in every game, 2012 on (nflverse), for quarterback values
  rosters_<season>.csv    each week's roster status, 2012 on (nflverse): who is on injured reserve
  snaps_<season>.csv      every player's share of snaps in every game, 2013 on (nflverse): who the starters are
  espn_odds.json          each book's pre-game close from ESPN, 2024 on (the answer key)
"""
import csv, json, pathlib, concurrent.futures as cf
from common import fetch

D = pathlib.Path("data")
REL = "https://github.com/nflverse/nflverse-data/releases/download"
SEASONS = range(2012, 2027)


def save(url, path):
    if not path.exists():
        body = fetch(url, as_json=False)
        if body is None:
            raise SystemExit(f"could not download {url}")
        path.write_bytes(body)


def num(v):
    if isinstance(v, dict):
        v = v.get("american") or v.get("alternateDisplayValue") or v.get("value")
    if v in (None, ""):
        return None
    if str(v).upper() == "EVEN":
        return 100.0
    try:
        return float(str(v).replace("+", "").lstrip("ouOU"))
    except ValueError:
        return None


def odds(espn_id):
    """Each book's pre-game line for one game. ESPN keeps in-game odds under '... - Live Odds'."""
    d = fetch(f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{espn_id}"
              f"/competitions/{espn_id}/odds?limit=50")
    books = {}
    for it in (d or {}).get("items", []):
        name = (it.get("provider") or {}).get("name") or ""
        if "Live" in name:
            continue
        h, a = it.get("homeTeamOdds") or {}, it.get("awayTeamOdds") or {}
        rec = {"spread": num(it.get("spread")), "total": num(it.get("overUnder"))}
        for when in ("open", "close"):
            rec[f"{when}_total"] = num((it.get(when) or {}).get("total"))
            rec[f"{when}_spread"] = num((h.get(when) or {}).get("pointSpread"))
            rec[f"{when}_ml_home"] = num((h.get(when) or {}).get("moneyLine"))
            rec[f"{when}_ml_away"] = num((a.get(when) or {}).get("moneyLine"))
        books[name] = rec
    return espn_id, books


if __name__ == "__main__":
    D.mkdir(exist_ok=True)
    save("https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv", D / "games.csv")
    for s in SEASONS:
        save(f"{REL}/injuries/injuries_{s}.csv", D / f"injuries_{s}.csv")
        save(f"{REL}/stats_player/stats_player_week_{s}.csv", D / f"stats_{s}.csv")
        save(f"{REL}/weekly_rosters/roster_weekly_{s}.csv", D / f"rosters_{s}.csv")
        if s >= 2013:
            save(f"{REL}/snap_counts/snap_counts_{s}.csv", D / f"snaps_{s}.csv")
    games = [g for g in csv.DictReader(open(D / "games.csv")) if int(g["season"]) >= 2024 and g["espn"] and g["result"]]
    path = D / "espn_odds.json"
    out = json.loads(path.read_text()) if path.exists() else {}
    with cf.ThreadPoolExecutor(8) as ex:
        out.update(dict(ex.map(odds, [g["espn"] for g in games if not out.get(g["espn"])])))
    path.write_text(json.dumps(out))
    print(len(out), "games with ESPN odds,", sum(not v for v in out.values()), "without")
