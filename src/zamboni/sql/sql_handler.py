from collections import defaultdict
import logging
import pandas as pd
from zamboni.db_con import DBConnector
from zamboni.sport import Game, TeamService
from zamboni.utils import split_csv_line
from zamboni.utils import today_date_str
from zamboni.sql.export_statements import export_statements

logger = logging.getLogger(__name__)
today_date = today_date_str()


class SQLHandler:
    """Load information from text files into SQLite database"""

    def __init__(self, txt_dir="data", db_con=None):
        """
        Establish connection to db
        """
        self.txt_dir = txt_dir
        if not db_con:
            db_connector = DBConnector()
            self.db_con = db_connector.connect_db()
        else:
            self.db_con = db_con
        self.team_id_dict = defaultdict(lambda: "Undefined")

    def execute(self, sql):
        """
        Execute SQL statement
        """
        with self.db_con as cursor:
            out = cursor.execute(sql)
        self.db_con.commit()
        return out

    def get_team_id(self, id_dict, team_abbrev):
        """
        Get team ID from db if it exists and store in dictionary if not
        """
        if id_dict[team_abbrev] == "Undefined":
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

    def check_game_exists(self, game):
        """
        Check if game exists in db
        """
        sql = f"SELECT apiID, outcome FROM games WHERE apiID={game.api_id} "
        with self.db_con as cursor:
            query_res = cursor.execute(sql)
        return query_res.fetchone()

    def insert_game(self, game):
        """
        Insert game into db
        """
        sql = f'''INSERT INTO games(apiId, seasonID, homeTeamID, awayTeamID, datePlayed, dayOfYrPlayed, yrPlayed, timePlayed, homeTeamGoals, awayTeamGoals, gameTypeID, lastPeriodTypeID, outcome, inOT, recordCreated)
                    VALUES("{game.api_id}", \
                           "{getattr(game, "season_id", 0)}", \
                           "{getattr(game, "home_team_id", -1)}", \
                           "{getattr(game, "away_team_id", -1)}", \
                           "{getattr(game, "date_played")}", \
                           "{getattr(game, "day_of_year_played")}", \
                           "{getattr(game, "year_played")}", \
                           "{getattr(game, "time_played")}", \
                           "{getattr(game, "home_team_goals")}", \
                           "{getattr(game, "away_team_goals")}", \
                           "{getattr(game, "game_type_id")}", \
                           "{getattr(game, "last_period_type_id")}", \
                           "{getattr(game, "outcome")}", \
                           "{getattr(game, "in_ot")}", \
                           "{today_date}"
                           )'''
        with self.db_con as cursor:
            cursor.execute(sql)

    def update_game(self, game, cursor):
        """
        Update game in db
        """
        sql = f'''UPDATE games
                    SET homeTeamGoals="{game.home_team_goals}",
                        awayTeamGoals="{game.away_team_goals}",
                        outcome="{game.outcome}",
                        inOT="{game.in_ot}",
                        lastPeriodTypeID="{game.last_period_type_id}"
                    WHERE apiID="{game.api_id}"'''
        cursor.execute(sql)

    def load_games_to_db(self, txt_path=None, overwrite=False):
        """
        Load games from txt to db
        """
        team_service = TeamService(self.db_con)
        if not txt_path:
            txt_path = f"{self.txt_dir}/games.txt"
        with open(txt_path, "r") as f, self.db_con as cursor:
            for line in f.readlines():
                game = Game.from_csv_line(line)
                game.team_ids_from_abbrev(team_service)
                exists_out = self.check_game_exists(game)
                if not exists_out:
                    self.insert_game(game)
                else:
                    api_id, outcome = exists_out
                    if outcome == -1 or overwrite:
                        self.update_game(game, cursor)
                    else:
                        logger.debug(
                            f"Game with ID {api_id} already exists in db with outcome {outcome}, skipping"
                        )
        txt_path = f"{self.txt_dir}/games_today.txt"
        with open(txt_path, "r") as f, self.db_con as cursor:
            for line in f.readlines():
                game = Game.from_csv_line(line)
                game.team_ids_from_abbrev(team_service)
                exists_out = self.check_game_exists(game)
                if not exists_out:
                    self.insert_game(game)
                else:
                    logger.debug(
                        f"Game with ID {api_id} already exists in db with outcome {outcome}, skipping"
                    )

    def load_players(self, txt_path=None):
        """
        Load players from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/players.txt"
        with open(txt_path) as f, self.db_con as cursor:
            for line in f.readlines():
                api_id, full_name, first_name, last_name, number, position = (
                    split_csv_line(line)
                )
                sql = f'''INSERT INTO players(apiID, name, firstName, lastName, number, position)
                        VALUES("{api_id}", "{full_name}", "{first_name}", "{last_name}", "{number}", "{position}")'''
                cursor.execute(sql)
            self.db_connector.conn.commit()

    def load_roster_entries(self, txt_path=None):
        """
        Load roster entries (player + team + season) from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/rosterEntries.txt"
        with open(txt_path, "r") as f, self.db_con as cursor:
            for line in f.readlines():
                line = [entry.strip() for entry in line.split(",")]
                (
                    api_id,
                    team_abbrev,
                    year,
                    first_name,
                    last_name,
                    start_year,
                    end_year,
                ) = line

                team_id_sql = (
                    f'''SELECT id FROM teams WHERE nameAbbrev="{team_abbrev}"'''
                )
                team_id_res = cursor.execute(team_id_sql)
                team_id_fetch = team_id_res.fetchone()
                if team_id_fetch is None:
                    print("No team found with name {team_abbrev}, skipping record")
                    continue
                team_id = team_id_fetch[0]

                player_id_sql = f'''SELECT id FROM players WHERE firstName="{first_name}" AND lastName="{last_name}"'''
                player_id_res = cursor.execute(player_id_sql)
                player_id_fetch = player_id_res.fetchone()
                if player_id_fetch is None:
                    print(
                        f"No player found with name {first_name} {last_name}, skipping record"
                    )
                    continue
                player_id = player_id_fetch[0]

                sql = f'''INSERT INTO rosterEntries(apiID, playerID, teamID, seasonID, startYear, endYear)
                        VALUES("{api_id}", "{player_id}", "{team_id}", "{year}", "{start_year}", "{end_year}")'''
                cursor.execute(sql)

    def load_teams(self, txt_path=None):
        """
        Load teams from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/teams.txt"
        with open(txt_path, "r") as f, self.db_con as cursor:
            delete_sql = """DELETE FROM teams"""
            cursor.execute(delete_sql)
            for line in f.readlines():
                team_name, name_abbrev, conf_abbrev, div_abbrev = split_csv_line(line)
                sql = f'''INSERT INTO teams(name, nameAbbrev, conferenceAbbrev, divisionAbbrev)
                        VALUES("{team_name}", "{name_abbrev}", "{conf_abbrev}", "{div_abbrev}")'''
                cursor.execute(sql)

    def query(self, sql):
        """
        Query the database with the given SQL statement

        :param sql: SQL statement to query information from db
        :return: DataFrame with queried data
        """
        df = pd.read_sql(sql, self.db_con)
        return df

    def query_games(self, start_date=None, end_date=today_date):
        """
        Export games information with recency selection
        """
        export_sql = export_statements["games"]
        # If start_date given, filter for only games after this date
        if not start_date:
            export_sql += f'WHERE games.datePlayed <= "{end_date}" '
        else:
            export_sql += f'WHERE games.datePlayed <= "{end_date}" '
            export_sql += f'AND games.datePlayed >= "{start_date}" '
        logger.debug(export_sql)
        games = self.query(export_sql)
        return games

    def query_games_with_predictions(self, start_date, end_date=None):
        """
        Export games with predictions information with recency selection
        """
        if end_date is None:
            end_date = start_date
        export_sql = export_statements["games_with_predictions"]
        export_sql = export_sql.format(start_date=start_date, end_date=end_date)
        logger.debug(export_sql)
        games_with_preds = self.query(export_sql)
        return games_with_preds

    def get_earliest_date_played(self):
        """
        Get game in db with earliest datePlayed.
        """
        games = self.query_games()
        games_ordered = games.sort_values(by="datePlayed")
        earliest_date = games_ordered["datePlayed"][0]
        return pd.to_datetime(earliest_date)

    def record_game_prediction(self, game_id, predicter_id, prediction):
        """
        Log a game prediction to the database
        """
        # Use ON CONFLICT to update if the gameID and predicterID already exist
        prediction_bin = int(prediction > 0.5)
        sql = f'''INSERT INTO gamePredictions(gameID, predicterID, prediction, predictionBinary, predictionDate)
                  VALUES("{game_id}", "{predicter_id}", "{prediction}", "{prediction_bin}", "{today_date}")
                  ON CONFLICT(gameID, predicterID) 
                  DO UPDATE SET prediction="{prediction}", predictionBinary="{prediction_bin}", predictionDate="{today_date}"'''
        with self.db_con as cursor:
            cursor.execute(sql)

    def add_predicter_to_register(
        self, name, predicter_class_name, path="", trainable=False, active=True
    ):
        """
        Register a new predicter in the predicterRegister table
        """
        # Use ON CONFLICT to update if the predicterName already exists
        register_sql = f'''INSERT INTO predicterRegister(predicterName, predicterType, predicterPath, trainable, active)
                VALUES("{name}", "{predicter_class_name}", "{path}", "{int(trainable)}", "{int(active)}")
                ON CONFLICT(predicterName) 
                DO UPDATE SET predicterType="{predicter_class_name}", predicterPath="{path}", trainable="{int(trainable)}", active="{int(active)}"'''
        with self.db_con as cursor:
            cursor.execute(register_sql)

    def predicter_id_from_name(self, predicter_name):
        read_register_id_sql = f'''SELECT id FROM predicterRegister WHERE predicterName="{predicter_name}"'''
        with self.db_con as cursor:
            query_res = cursor.execute(read_register_id_sql)
        fetched = query_res.fetchone()
        if not fetched:
            raise ValueError(
                f"Could not retrieve new predicter ID from predicterRegister with name {predicter_name}"
            )
        else:
            predicter_id = fetched[0]
        return predicter_id

    def add_predicter_to_last_training(self, predicter_id):
        last_training_sql = f"""INSERT INTO lastTraining(predicterID, lastTrainingDate)
                VALUES({predicter_id}, NULL)"""
        with self.db_con as cursor:
            _ = cursor.execute(last_training_sql)

    def set_action_date(self, table_name, column_name, update_date=today_date):
        """
        Set the date in a table tracking last action taken
        """
        delete_sql = f"""DELETE FROM {table_name}"""
        insert_sql = (
            f'''INSERT INTO {table_name}({column_name}) VALUES("{update_date}")'''
        )
        with self.db_con as cursor:
            cursor.execute(delete_sql)
            cursor.execute(insert_sql)

    def get_action_date(self, table_name, column_name):
        """
        Read the action date from a table
        """
        select_sql = f"""SELECT {column_name} FROM {table_name} LIMIT 1"""
        with self.db_con as cursor:
            query_res = cursor.execute(select_sql)
        fetched = query_res.fetchone()
        if fetched:
            out = fetched[0]
        else:
            out = None
        return out

    def set_game_export_date(self):
        """
        Update the date in gamesLastExport with current date
        """
        self.set_action_date("gamesLastExport", "lastExportDate")

    def get_game_export_date(self):
        """
        Read the date in gamesLastExport
        """
        out = self.get_action_date("gamesLastExport", "lastExportDate")
        return out

    def set_last_training_date(self, predicter_id):
        """
        Update the date in lastTraining with current date
        """
        # Use ON CONFLICT to update if the gameID and predicterID already exist
        sql = f'''INSERT INTO lastTraining(predicterID, lastTrainingDate)
                  VALUES("{predicter_id}", "{today_date}")
                  ON CONFLICT(predicterID) 
                  DO UPDATE SET lastTrainingDate="{today_date}"'''
        with self.db_con as cursor:
            cursor.execute(sql)

    def get_last_training_date(self, predicter_id):
        """
        Read the date in lastTraining
        """
        select_sql = f'''SELECT lastTrainingDate FROM lastTraining WHERE predicterID="{predicter_id}" LIMIT 1'''
        with self.db_con as cursor:
            query_res = cursor.execute(select_sql)
        fetched = query_res.fetchone()
        if fetched:
            out = fetched[0]
        else:
            out = None
        return out

    def get_last_prediction_date(self, predicter_id):
        """
        Read the date in lastTraining
        """
        select_sql = f'''SELECT MAX(predictionDate) FROM gamePredictions WHERE predicterID="{predicter_id}"'''
        with self.db_con as cursor:
            query_res = cursor.execute(select_sql)
        fetched = query_res.fetchone()
        if fetched:
            out = fetched[0]
        else:
            out = None
        return out

    def get_predicters(self):
        """
        Get the predicters from the db
        """
        sql = "SELECT id, predicterName, predicterType, predicterPath, trainable, active FROM predicterRegister"
        with self.db_con as cursor:
            query_res = cursor.execute(sql)
        out = [list(row) for row in query_res.fetchall()]
        return out
