import requests
import json
from zamboni import DBConnector

connector = DBConnector('zamboni.db')
connector.connect_db()
connector.close()

#r = requests.get('https://api-web.nhle.com/v1/club-schedule-season/DET/now')
#info_json = r.json()
#for key, value in info_json.items():
#    print(key)
#    print(value)
