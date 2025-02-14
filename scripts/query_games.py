import requests
from datetime import datetime, date, timedelta

from zamboni import APICaller

sched_date = date(2024, 2, 7)
day_delta = timedelta(days=1)

caller = APICaller()

out = caller.query('game', [sched_date])
print(out['gameWeek'])
