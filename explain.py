"""Show how the final model priced one game, piece by piece.
Usage: python3 explain.py AWAY HOME YYYY-MM-DD      e.g.  python3 explain.py SF NO 2025-09-14"""
import sys
from data import load, window
from model import run, tuned_models

away, home, day = sys.argv[1], sys.argv[2], sys.argv[3]
games = load()
g = next(g for g in games if g["home"] == home and g["away"] == away and g["date"] == day)
trace = {}
run(games, **tuned_models(games, window(g["season"]), "line")["+ division games"], trace=trace)
t = trace[g["id"]]
print(f"\n{away} at {home}, {day}  (positive = {home} favoured; settings chosen on {window(g['season'])[0]} to {window(g['season'])[-1]})\n")
print(f"  team ratings                               {t['team']:+.1f}")
print(f"  home field                                 {t['home_court']:+.1f}")
print(f"  rest            {home} {g['home_rest']} days, {away} {g['away_rest']} days    {t['rest']:+.1f}")
print(f"  quarterbacks    {'starter out: ' + (home if g['home_qb_out'] else '') + (' ' + away if g['away_qb_out'] else '') if g['home_qb_out'] or g['away_qb_out'] else 'no change':<26} {t['qb'] + t['qb_level']:+.1f}")
print(f"  other injuries  starters out: {home} {g['home_starters_out']:.2f}, {away} {g['away_starters_out']:.2f}  {t['injuries']:+.1f}")
print(f"  division game   {'yes' if g['div'] else 'no'}")
print(f"  {'-' * 50}")
close = f"{home} by {-g['close']:+.1f} ({g['book']})" if g["close"] is not None else "none recorded"
print(f"  MODEL: {home} by {t['total']:+.1f}   CLOSE: {close}   RESULT: {home} by {g['margin']:+d}")
