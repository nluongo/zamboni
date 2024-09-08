import requests
from datetime import datetime
from zamboni import APICaller

caller = APICaller('roster')

with open('data/teams.txt', 'r') as f_teams:
    team_lines = f_teams.readlines()
    team_lines = [line.split(',') for line in team_lines]
    team_abbrevs = [line[1].strip() for line in team_lines]

start_year = 1900
end_year = start_year + 1

with open('data/rosterEntries.txt', 'a') as roster_f:
    while start_year < datetime.now().year:
        end_year = start_year + 1
        for team in team_abbrevs:
            api_ids = [team, start_year, end_year]
            out = caller.query(api_ids, throw_error=False)
            if out is None:
                continue
            forwards = info_json['forwards']
            defensemen = info_json['defensemen']
            goalies = info_json['goalies']
            players = forwards + defensemen + goalies
            for player in players:
                print(player)
                first_name = player['firstName']['default']
                last_name = player['lastName']['default']
                api_id = player['id']
                entry_str = f'{api_id}, {team}, {start_year}, {first_name}, {last_name}, {start_year}, {end_year}\n'
                roster_f.write(entry_str)
        start_year += 1
