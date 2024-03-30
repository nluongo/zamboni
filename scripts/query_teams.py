import requests

r = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
info_json = r.json().get('teams', [])
print(info_json)
exit()
week = info_json['gameWeek']
day = week[0]
print(day['date'])
for game in day['games']:
    print()
    for key, value in game.items():
        print(key)
        print(value)
