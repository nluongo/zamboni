from zamboni import APICaller
import logging

logging.basicConfig(level='INFO')

def download_games():
    from datetime import datetime, date, timedelta
    
    caller = APICaller('game')
    
    # Per Wikipedia, the first NHL game
    #sched_date = date(1917, 12, 19)
    # Do not download entire history during R&D phase
    sched_date = date(2020, 7, 1)
    day_delta = timedelta(days=1)
    
    today_date = date.today()
    
    def zero_pad(to_pad, length, padder='0'):
        padded_value = padder * (length - len(str(to_pad))) + str(to_pad)
        return padded_value
    
    with open('data/games.txt', 'a+') as f:
        f.seek(0)
        lines = f.readlines()
        if len(lines) > 0:
            for line in lines:
                pass
            last_line = line
            date = last_line.split(',')[4].strip()
            last_date = datetime.fromisoformat(date).date()
            sched_date = last_date + day_delta
        while sched_date <= today_date:
            year_str = zero_pad(sched_date.year, 4)
            month_str = zero_pad(sched_date.month, 2)
            day_str = zero_pad(sched_date.day, 2)
            date_string = f'{year_str}-{month_str}-{day_str}'
            logging.info(f'Querying API at date {date_string}')
            output = caller.query([date_string], throw_error=False)
            if not output:
                sched_date += day_delta
                continue
            week = output['gameWeek']
            for day in week:
                date = day['date']
                games = day['games']
                if games == []:
                    logging.info(f'No games found for date {date}')
                    sched_date += day_delta
                    continue
                for game in day['games']:
                    try:
                        api_id = game['id']
                        season_id = game['season']
                        datetime.fromisoformat('2011-11-04T00:05:23')
                        datetime_utc = datetime.fromisoformat(game['startTimeUTC'].replace('Z','+00:00'))
                        day_of_yr = datetime_utc.timetuple().tm_yday
                        year = sched_date.year
                        home_team = game['homeTeam']
                        home_id = home_team['id']
                        home_abbrev = home_team['abbrev']
                        home_goals = home_team['score']
                        away_team = game['awayTeam']
                        away_id = away_team['id']
                        away_abbrev = away_team['abbrev']
                        away_goals = away_team['score']
                        type_id = game['gameType']
                        last_period_type = game['gameOutcome']['lastPeriodType']
                    except KeyError:
                        logging.info(f'Error getting data for date {date}')
                        continue
                    f.write(f'{api_id}, {season_id}, {home_id}, {home_abbrev}, {away_id}, {away_abbrev}, {datetime_utc.date()}, {day_of_yr}, {year}, {datetime_utc.time()}, {home_goals}, {away_goals}, {type_id}, {last_period_type}\n')
                sched_date += day_delta

def download_players():
    caller = APICaller('player')
    
    #api_id = 8475104
    api_id = 8440000
    # Less than 2500 players in the league
    #end_id = 8477604
    end_id = 8500000
    fetch_players = 1
    step = 1
    with open('data/players.txt', 'w') as f:
        while api_id < end_id:
            player = caller.query([api_id], throw_error=False)
            if not player:
                if api_id%step == 0:
                    print(api_id)
                api_id += 1
                continue
            first_name = player['firstName']['default']
            last_name = player['lastName']['default']
            full_name = f'{first_name} {last_name}'
            if 'sweaterNumber' not in player.keys():
                number = '-1'
            else:
                number = str(player['sweaterNumber'])
            if 'position' not in player.keys():
                position = 'U'
            else:
                position = player['position']
            write_string = ','.join([str(api_id), full_name, first_name, last_name, number, position])
            f.write(write_string+'\n')
            api_id += 1

def download_rosters():
    from datetime import datetime
    
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
                forwards = out['forwards']
                defensemen = out['defensemen']
                goalies = out['goalies']
                players = forwards + defensemen + goalies
                for player in players:
                    print(player)
                    first_name = player['firstName']['default']
                    last_name = player['lastName']['default']
                    api_id = player['id']
                    entry_str = f'{api_id}, {team}, {start_year}, {first_name}, {last_name}, {start_year}, {end_year}\n'
                    roster_f.write(entry_str)
            start_year += 1

def download_teams():
    caller = APICaller('standings')
    
    info_json = caller.query()
    
    standings = info_json['standings']
    with open('data/teams.txt', 'w') as f:
        for team in standings:
            team_name = team['teamName']['default']
            team_abbrev = team['teamAbbrev']['default']
            conf_abbrev = team['conferenceAbbrev']
            div_abbrev = team['divisionAbbrev']
            team_str = f'{team_name}, {team_abbrev}, {conf_abbrev}, {div_abbrev}\n'
            f.write(team_str)
