import requests
from datetime import datetime, date, timedelta

from zamboni import APICaller

sched_date = date(2024, 11, 5)
day_delta = timedelta(days=1)

caller = APICaller('game')

out = caller.query([sched_date])
print(out)
