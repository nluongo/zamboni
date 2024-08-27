from zamboni.db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

with open('data/rosterEntries.txt', 'r') as f:

    for line in f.readlines():
        line = [entry.strip() for entry in line.split(',')]
        api_id, team_abbrev, year, first_name, last_name, start_year, end_year = line

        team_id_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
        team_id_res = cursor.execute(team_id_sql)
        team_id_fetch = team_id_res.fetchone()
        if team_id_fetch is None:
            print('No team found with name {team_abbrev}, skipping record')
            continue
        team_id = team_id_fetch[0]

        player_id_sql = f'''SELECT id FROM players WHERE firstName="{first_name}" AND lastName="{last_name}"'''
        player_id_res = cursor.execute(player_id_sql)
        player_id_fetch = player_id_res.fetchone()
        if player_id_fetch is None:
            print(f'No player found with name {first_name} {last_name}, skipping record')
            continue
        player_id = player_id_fetch[0]

        sql = f'''INSERT INTO rosterEntries(apiID, playerID, teamID, seasonID, startYear, endYear)
                VALUES("{api_id}", "{player_id}", "{team_id}", "{year}", "{start_year}", "{end_year}")'''
        cursor.execute(sql)
        conn.commit()
