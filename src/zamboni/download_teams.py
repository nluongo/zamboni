from zamboni import APICaller

caller = APICaller()

info_json = caller.query('standings', 'now')

standings = info_json['standings']
with open('data/teams.txt', 'w') as f:
    for team in standings:
        team_name = team['teamName']['default']
        team_abbrev = team['teamAbbrev']['default']
        conf_abbrev = team['conferenceAbbrev']
        div_abbrev = team['divisionAbbrev']
        team_str = f'{team_name}, {team_abbrev}, {conf_abbrev}, {div_abbrev}\n'
        f.write(team_str)


