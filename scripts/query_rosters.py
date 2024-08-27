import requests

team_abbrev = 'DET'
start_year = 2019
end_year = 2020
r = requests.get(f'https://api-web.nhle.com/v1/roster/{team_abbrev}/{start_year}{end_year}')
info_json = r.json()
print(info_json)
forwards = info_json['forwards']
defensemen = info_json['defensemen']
goalies = info_json['goalies']
players = forwards + defensemen + goalies

for player in players:
    print(player)
    first_name = player['firstName']['default']
    last_name = player['lastName']['default']
    api_id = player['id']
    print(f'{team_abbrev} {start_year} {first_name} {last_name} {api_id}')

