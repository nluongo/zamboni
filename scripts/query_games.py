import requests
from datetime import datetime, date, timedelta

sched_date = date(2022, 9, 28)
day_delta = timedelta(days=1)

today_date = date.today()

with open('data/games.txt', 'a') as f:
    while sched_date <= today_date:
        year_str = '0'*(4-len(str(sched_date.year))) + str(sched_date.year)
        month_str = '0'*(2-len(str(sched_date.month))) + str(sched_date.month)
        day_str = '0'*(2-len(str(sched_date.day))) + str(sched_date.day)
        date_string = f'{year_str}-{month_str}-{day_str}'
        print(date_string)
        try:
            request_string = f'https://api-web.nhle.com/v1/schedule/{date_string}'
            print(request_string)
            r = requests.get(request_string)
            info_json = r.json()
        except:
            sched_date += day_delta
            continue
        week = info_json['gameWeek']
        day = week[0]
        for day in week:
            print(day)
        print(day['date'])
        for game in day['games']:
            print()
            api_id = game['id']
            season_id = game['season']
            print(f'api_id: {api_id}')
            print(f'season_id: {season_id}')
            datetime.fromisoformat('2011-11-04T00:05:23')
            datetime_utc = datetime.fromisoformat(game['startTimeUTC'].replace('Z','+00:00'))
            print(f'datetime_utc: {datetime_utc}')
            print(f'date_utc: {datetime_utc.date()}')
            print(f'time_utc: {datetime_utc.time()}')
            home_team = game['homeTeam']
            home_id = home_team['id']
            home_goals = home_team['score']
            away_team = game['awayTeam']
            away_id = away_team['id']
            away_goals = away_team['score']
            type_id = game['gameType']
            last_period_type = game['gameOutcome']['lastPeriodType']
            for key, value in game.items():
                print(key)
                print(value)
            print(f'{api_id}, {home_id}, {away_id}, {datetime_utc.date()}, {datetime_utc.time()}, {home_goals}, {away_goals}, {type_id}, {last_period_type}')
        break
        sched_date += day_delta
    
