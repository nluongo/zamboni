import requests
from zamboni import APICaller

caller = APICaller('player')

#api_id = 8475104
api_id = 8450157
# Less than 2500 players in the league
out = caller.query([api_id])
print(out)
