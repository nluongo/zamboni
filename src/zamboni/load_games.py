from zamboni.db_con import DBConnector
from collections import defaultdict

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

team_id_dict = defaultdict(lambda: 'Undefined')

def get_team_id(id_dict, team_abbrev):
    if id_dict[team_abbrev] == 'Undefined':
        query_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
        query_res = cursor.execute(query_sql)
        query_out = query_res.fetchone()
        if query_out:
            team_id = query_out[0]
            id_dict[team_abbrev] = team_id
        else:
            team_id = -1
    else:
        team_id = id_dict[team_abbrev]
    return team_id
    
with open('data/games.txt', 'r') as f:
    for line in f.readlines():
        split_line = line.split(',')
        split_line = [entry.strip() for entry in split_line]
        api_id, season_id, home_api_id, home_team_abbrev, away_api_id, away_team_abbrev, date_played, day_of_year_played, year_played, time_played, home_team_goals, away_team_goals, game_type, last_period_type = split_line
        home_team_id = get_team_id(team_id_dict, home_team_abbrev)
        away_team_id = get_team_id(team_id_dict, away_team_abbrev)
        if home_team_goals > away_team_goals:
            outcome = 1
        elif home_team_goals < away_team_goals:
            outcome = 0
        else:
            outcome = -1
        if last_period_type == 'REG':
            in_ot = 0
        else:
            in_ot = 1
        sql = f'''INSERT INTO games(apiId, seasonID, homeTeamID, awayTeamID, datePlayed, dayOfYrPlayed, yrPlayed, timePlayed, homeTeamGoals, awayTeamGoals, gameTypeID, lastPeriodTypeID, outcome, inOT)
                VALUES("{api_id}", \
                       "{season_id}", \
                       "{home_team_id}", \
                       "{away_team_id}", \
                       "{date_played}", \
                       "{day_of_year_played}", \
                       "{year_played}", \
                       "{time_played}", \
                       "{home_team_goals}", \
                       "{away_team_goals}", \
                       "{game_type}", \
                       "{last_period_type}", \
                       "{outcome}", \
                       "{in_ot}" \
                       )'''
        cursor.execute(sql)
        conn.commit()
