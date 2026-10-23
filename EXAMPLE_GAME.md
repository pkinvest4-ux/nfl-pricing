# One game, start to finish

**San Francisco 49ers at New Orleans Saints, September 14, 2025 (week 2).** This is how the final model
built its number the day before. Positive numbers favour New Orleans. Made with
`python3 explain.py SF NO 2025-09-14`.

| Part | What it says | Points |
|---|---|---|
| Team ratings | San Francisco rated well above New Orleans | **-6.3** |
| Home field | New Orleans at home | **+1.5** |
| Rest | Both teams on 7 days | **0.0** |
| Quarterbacks | Brock Purdy listed Out on the final injury report, so a backup is expected to start | **+3.1** |
| Other injuries | New Orleans has more starters listed | **-0.3** |
| Division game | No | |
| **Model** | | **San Francisco by 2.1** |
| **Close (ESPN BET)** | | **San Francisco by 2.5** |
| **Result** | | **San Francisco by 5** |

Without the quarterback step, the model would have had San Francisco by about 5. Purdy being out moved it
3 points, to within 0.4 of the close. The quarterback step is the second-biggest improvement in the model.
