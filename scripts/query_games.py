import requests

r = requests.get('https://api-web.nhle.com/v1/schedule/2023-09-23')
info_json = r.json()
week = info_json['gameWeek']
day = week[0]
print(day['date'])
for game in day['games']:
    print()
    for key, value in game.items():
        print(key)
        print(value)
