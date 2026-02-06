from datetime import date, timedelta
from pprint import pprint
import requests
from zamboni.utils import zero_pad_date
from zamboni import APICaller

year = 2026
month = 1
day = 24
sched_date = date(year, month, day)
day_delta = timedelta(days=1)

caller = APICaller()

date_str = zero_pad_date(year, month, day)

#out = caller.query([sched_date], "game")
url = caller.query_url([sched_date], "game")
out = requests.get(url).json()
pprint(out)
#game_week = out["gameWeek"]
#pprint(game_week)
#day_0 = game_week[0]
#pprint(day_0)
#game_0 = day_0["games"][0]
#pprint(game_0)
#game_week = out["gameWeek"]
#for game_date in game_week:
#    if game_date["date"] == date_str:
#        for game in game_date["games"]:
#            print(game["homeTeam"]["commonName"]["default"])
#            print(game["awayTeam"]["commonName"]["default"])
#            print()
