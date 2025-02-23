from zamboni.db_con import DBConnector
from collections import defaultdict

class SQLLoader():
    ''' Load information from text files into SQLite database '''
    def __init__(self, txt_dir='data', db_con=None):
        '''
        Establish connection to db
        '''
        self.txt_dir = txt_dir
        if not db_con:
            db_connector = DBConnector()
            self.db_con = db_connector.connect_db()
        else:
            self.db_con = db_con
        self.team_id_dict = defaultdict(lambda: 'Undefined')

    def get_team_id(self, id_dict, team_abbrev):
        ''' 
        Get team ID from db if it exists and store in dictionary if not 
        '''
        if id_dict[team_abbrev] == 'Undefined':
            query_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
            with self.db_con as cursor:
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
    
    def load_games(self, txt_path=None):
        '''
        Load games from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/games.txt'
        with open(txt_path, 'r') as f, self.db_con as cursor:
            for line in f.readlines():
                split_line = line.split(',')
                split_line = [entry.strip() for entry in split_line]
                api_id, season_id, home_api_id, home_team_abbrev, away_api_id, away_team_abbrev, date_played, day_of_year_played, year_played, time_played, home_team_goals, away_team_goals, game_type, last_period_type = split_line
                home_team_id = self.get_team_id(self.team_id_dict, home_team_abbrev)
                away_team_id = self.get_team_id(self.team_id_dict, away_team_abbrev)
                if home_team_goals > away_team_goals:
                    outcome = 1
                elif home_team_goals < away_team_goals:
                    outcome = 0
                else:
                    outcome = -1
                if last_period_type == 'OT':
                    in_ot = 1
                else:
                    in_ot = 0
                exists_sql = f'SELECT 1 FROM games ' \
                        f'WHERE apiID={api_id} ' \
                        f'AND seasonID={season_id} ' \
                        f'AND homeTeamID={home_team_id} ' \
                        f'AND awayTeamID={away_team_id} ' \
                        f'AND datePlayed="{date_played}" ' \
                        f'AND dayOfYrPlayed={day_of_year_played} ' \
                        f'AND yrPlayed={year_played} ' \
                        f'AND timePlayed="{time_played}" ' \
                        f'AND homeTeamGoals={home_team_goals} ' \
                        f'AND awayTeamGoals={away_team_goals} ' \
                        f'AND gameTypeID={game_type} ' \
                        f'AND lastPeriodTypeID="{last_period_type}" ' \
                        f'AND outcome={outcome} ' \
                        f'AND inOT={in_ot}'
                exists_res = cursor.execute(exists_sql).fetchone()
                if exists_res:
                    continue
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

    def load_players(self, txt_path=None):
        '''
        Load players from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/players.txt'
        with open(txt_path) as f, self.db_con as cursor:
            for line in f.readlines():
                line = [entry.strip() for entry in line.split(',')]
                api_id, full_name, first_name, last_name, number, position = line
                sql = f'''INSERT INTO players(apiID, name, firstName, lastName, number, position)
                        VALUES("{api_id}", "{full_name}", "{first_name}", "{last_name}", "{number}", "{position}")'''
                self.cursor.execute(sql)
            self.db_connector.conn.commit()
        
    def load_roster_entries(self, txt_path=None):
        '''
        Load roster entries (player + team + season) from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/rosterEntries.txt'
        with open(txt_path, 'r') as f, self.db_con as cursor:
            for line in f.readlines():
                line = [entry.strip() for entry in line.split(',')]
                api_id, team_abbrev, year, first_name, last_name, start_year, end_year = line
        
                team_id_sql = f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
                team_id_res = self.cursor.execute(team_id_sql)
                team_id_fetch = team_id_res.fetchone()
                if team_id_fetch is None:
                    print('No team found with name {team_abbrev}, skipping record')
                    continue
                team_id = team_id_fetch[0]
        
                player_id_sql = f'''SELECT id FROM players WHERE firstName="{first_name}" AND lastName="{last_name}"'''
                player_id_res = self.cursor.execute(player_id_sql)
                player_id_fetch = player_id_res.fetchone()
                if player_id_fetch is None:
                    print(f'No player found with name {first_name} {last_name}, skipping record')
                    continue
                player_id = player_id_fetch[0]
        
                sql = f'''INSERT INTO rosterEntries(apiID, playerID, teamID, seasonID, startYear, endYear)
                        VALUES("{api_id}", "{player_id}", "{team_id}", "{year}", "{start_year}", "{end_year}")'''
                self.cursor.execute(sql)

    def load_teams(self, txt_path=None):
        '''
        Load teams from txt to db
        '''
        if not txt_path:
            txt_path = f'{self.txt_dir}/teams.txt'
        with open(txt_path) as f, self.db_con as cursor:
            for line in f.readlines():
                split_line = line.split(',')
                split_line = [entry.strip() for entry in split_line]
                team_name, name_abbrev, conf_abbrev, div_abbrev = split_line
                sql = f'''INSERT INTO teams(name, nameAbbrev, conferenceAbbrev, divisionAbbrev)
                        VALUES("{team_name}", "{name_abbrev}", "{conf_abbrev}", "{div_abbrev}")'''
                cursor.execute(sql)
