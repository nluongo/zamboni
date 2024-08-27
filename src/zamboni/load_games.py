from zamboni.db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

with open('data/games.txt') as f:
    for line in f.readlines():
        split_line = line.split(',')
        split_line = [entry.strip() for entry in split_line]
        api_id, home_team_id, away_team_id, date_played, time_played, season_id, home_team_goals, away_team_goals, game_type, last_period_type = split_line
        sql = f'''INSERT INTO games(apiId, homeTeamID, awayTeamID, datePlayed, timePlayed, seasonID, homeTeamGoals, awayTeamGoals, gameTypeID, lastPeriodTypeID)
                VALUES("{api_id}", \
                       "{home_team_id}", \
                       "{away_team_id}", \
                       "{date_played}", \
                       "{time_played}", \
                       "{season_id}", \
                       "{home_team_goals}", \
                       "{away_team_goals}", \
                       "{game_type}", \
                       "{last_period_type}" \
                       )'''
        cursor.execute(sql)
        conn.commit()
