from zamboni.db_con import DBConnector

class SQLLoader():
    ''' Load information from text files into SQLite database '''
    def __init__(self, txt_dir='data', db_connector=None):
        '''
        Establish connection to db
        '''
        self.txt_dir = txt_dir
        if not db_connector:
            self.db_connector = DBConnector()
        else:
            self.db_connector = db_connector
        self.team_id_dict = defaultdict(lambda: 'Undefined')

    def get_team_id(id_dict, team_abbrev):
        ''' 
        Get team ID from db if it exists and store in dictionary if not 
        '''
        if id_dict[team_abbrev] == 'Undefined':
            query_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
            query_res = self.db_connector.cursor.execute(query_sql)
            query_out = query_res.fetchone()
            if query_out:
                team_id = query_out[0]
                id_dict[team_abbrev] = team_id
            else:
                team_id = -1
        else:
            team_id = id_dict[team_abbrev]
        return team_id
    
    def load_games(self, txt_path=None):
        '''
        Load games from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/games.txt'
        with open(txt_path, 'r') as f:
            for line in f.readlines():
                split_line = line.split(',')
                split_line = [entry.strip() for entry in split_line]
                api_id, season_id, home_api_id, home_team_abbrev, away_api_id, away_team_abbrev, date_played, day_of_year_played, year_played, time_played, home_team_goals, away_team_goals, game_type, last_period_type = split_line
                home_team_id = get_team_id(self.team_id_dict, home_team_abbrev)
                away_team_id = get_team_id(self.team_id_dict, away_team_abbrev)
                if home_team_goals > away_team_goals:
                    outcome = 1
                elif home_team_goals < away_team_goals:
                    outcome = 0
                else:
                    outcome = -1
                sql = f'''INSERT INTO games(apiId, seasonID, homeTeamID, awayTeamID, datePlayed, dayOfYrPlayed, yrPlayed, timePlayed, homeTeamGoals, awayTeamGoals, gameTypeID, lastPeriodTypeID, outcome)
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
                               "{outcome}" \
                               )'''
                self.db_connector.cursor.execute(sql)
            self.db_connector.conn.commit()

    def load_players(self, txt_path=None):
        '''
        Load players from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/players.txt'
        with open(txt_path) as f:
            for line in f.readlines():
                line = [entry.strip() for entry in line.split(',')]
                print(line)
                api_id, full_name, first_name, last_name, number, position = line
                sql = f'''INSERT INTO players(apiID, name, firstName, lastName, number, position)
                        VALUES("{api_id}", "{full_name}", "{first_name}", "{last_name}", "{number}", "{position}")'''
                self.db_connector.cursor.execute(sql)
            self.db_connector.conn.commit()
        
    def load_roster_entries(self, txt_path=None):
        '''
        Load roster entries (player + team + season) from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/rosterEntries.txt'
        with open(txt_path, 'r') as f:
            for line in f.readlines():
                line = [entry.strip() for entry in line.split(',')]
                api_id, team_abbrev, year, first_name, last_name, start_year, end_year = line
        
                team_id_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
                team_id_res = self.db_connector.cursor.execute(team_id_sql)
                team_id_fetch = team_id_res.fetchone()
                if team_id_fetch is None:
                    print('No team found with name {team_abbrev}, skipping record')
                    continue
                team_id = team_id_fetch[0]
        
                player_id_sql = f'''SELECT id FROM players WHERE firstName="{first_name}" AND lastName="{last_name}"'''
                player_id_res = self.db_connector.cursor.execute(player_id_sql)
                player_id_fetch = player_id_res.fetchone()
                if player_id_fetch is None:
                    print(f'No player found with name {first_name} {last_name}, skipping record')
                    continue
                player_id = player_id_fetch[0]
        
                sql = f'''INSERT INTO rosterEntries(apiID, playerID, teamID, seasonID, startYear, endYear)
                        VALUES("{api_id}", "{player_id}", "{team_id}", "{year}", "{start_year}", "{end_year}")'''
                self.db_connector.cursor.execute(sql)
            self.db_connector.conn.commit()

    def load_teams(self, txt_path=None):
        '''
        Load teams from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/teams.txt'
        with open(txt_path) as f:
            for line in f.readlines():
                split_line = line.split(',')
                split_line = [entry.strip() for entry in split_line]
                team_name, name_abbrev, conf_abbrev, div_abbrev = split_line
                sql = f'''INSERT INTO teams(name, nameAbbrev, conferenceAbbrev, divisionAbbrev)
                        VALUES("{team_name}", "{name_abbrev}", "{conf_abbrev}", "{div_abbrev}")'''
                self.db_connector.cursor.execute(sql)
            self.db_connector.conn.commit()
