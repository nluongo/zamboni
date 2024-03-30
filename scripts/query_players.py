import requests

r = requests.get('https://api-web.nhle.com/v1/score/now')
info_json = r.json()
week = info_json['gameWeek']
print(week[0])
for key in info_json['games'][0].keys():
    print(key)
game = info_json['games'][0]
goals = game['goals']
print(goals[0])
#r = requests.get('https://api-web.nhle.com/v1/player/8476453/landing')
r = requests.get('https://api-web.nhle.com/v1/player/8475104/landing')
player = r.json()
for key, value in player.items():
    print(key, value)
    print()

r = requests.get('https://api-web.nhle.com/v1/roster')
