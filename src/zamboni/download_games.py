from datetime import datetime, date, timedelta
from zamboni import APICaller

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
        date_string = [f'{year_str}-{month_str}-{day_str}']
        output = caller.query(date_string, throw_error=False)
        if not output:
            sched_date += day_delta
            continue
        week = output['gameWeek']
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
                home_abbrev = home_team['abbrev']
                home_goals = home_team['score']
                away_team = game['awayTeam']
                away_id = away_team['id']
                away_abbrev = away_team['abbrev']
                away_goals = away_team['score']
                type_id = game['gameType']
                last_period_type = game['gameOutcome']['lastPeriodType']
            except KeyError:
                sched_date += day_delta
                continue
            f.write(f'{api_id}, {season_id}, {home_id}, {home_abbrev}, {away_id}, {away_abbrev}, {datetime_utc.date()}, {datetime_utc.time()}, {home_goals}, {away_goals}, {type_id}, {last_period_type}\n')
        sched_date += day_delta
    
