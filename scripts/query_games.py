from datetime import date, timedelta
from zamboni.utils import zero_pad_date
from zamboni import APICaller

year = 2025
month = 5
day = 7
sched_date = date(year, month, day)
day_delta = timedelta(days=1)

caller = APICaller()

date_str = zero_pad_date(year, month, day)

out = caller.query([sched_date], "game")
game_week = out["gameWeek"]
for game_date in game_week:
    if game_date["date"] == date_str:
        for game in game_date["games"]:
            print(game["homeTeam"]["commonName"]["default"])
            print(game["awayTeam"]["commonName"]["default"])
            print()
