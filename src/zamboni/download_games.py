import requests
from datetime import datetime, date, timedelta

sched_date = date(2022, 9, 28)
day_delta = timedelta(days=1)

today_date = date.today()

def zero_pad(to_pad, length, padder='0'):
    padded_value = padder * (length - len(str(to_pad))) + str(to_pad)
    return padded_value

with open('data/games.txt', 'a') as f:
    while sched_date <= today_date:
        year_str = zero_pad(sched_date.year, 4)
        month_str = zero_pad(sched_date.month, 2)
        day_str = zero_pad(sched_date.day, 2)
        date_string = f'{year_str}-{month_str}-{day_str}'
        print(date_string)
        request_string = f'https://api-web.nhle.com/v1/schedule/{date_string}'
        try:
            r = requests.get(request_string)
            info_json = r.json()
        except:
            sched_date += day_delta
            continue
        week = info_json['gameWeek']
        day = week[0]
        games = day['games']
        if games == []:
            sched_date += day_delta
            continue
        for game in day['games']:
            try:
                api_id = game['id']
                season_id = game['season']
                datetime.fromisoformat('2011-11-04T00:05:23')
                datetime_utc = datetime.fromisoformat(game['startTimeUTC'].replace('Z','+00:00'))
                home_team = game['homeTeam']
                home_id = home_team['id']
                home_goals = home_team['score']
                away_team = game['awayTeam']
                away_id = away_team['id']
                away_goals = away_team['score']
                type_id = game['gameType']
                last_period_type = game['gameOutcome']['lastPeriodType']
            except:
                sched_date += day_delta
                continue
            f.write(f'{api_id}, {home_id}, {away_id}, {datetime_utc.date()}, {datetime_utc.time()}, {home_goals}, {away_goals}, {type_id}, {last_period_type}\n')
        sched_date += day_delta
    
