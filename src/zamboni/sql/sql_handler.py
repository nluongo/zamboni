from collections import defaultdict
from datetime import datetime
import logging
import pandas as pd
from sqlalchemy import select, insert, update, text, func
from sqlalchemy.exc import IntegrityError
from .tables import (
    Teams,
    Games,
    Players,
    RosterEntries,
    PredicterRegister,
    GamePredictions,
    LastTraining,
    Seasons,
)
from .sql_helpers import upsert
from zamboni.db_con import DBConnector
from zamboni.sport import Game
from zamboni.utils import split_csv_line, get_today_date, date_str_to_py
from zamboni.sql.statements import games_with_predictions_select, games_select


logger = logging.getLogger(__name__)
today_date = get_today_date()

# Allow-list for tables/columns that may be used with set_action_date/get_action_date
_ALLOWED_ACTION_TABLE_COLUMNS = {
    "gamesLastExport": {"lastExportDate"},
    "lastTraining": {"lastTrainingDate"},
}


class SQLHandler:
    """Load information from text files into SQLite database"""

    def __init__(self, txt_dir="data", engine=None):
        """
        Establish connection to db
        """
        self.txt_dir = txt_dir
        if not engine:
            db_connector = DBConnector()
            self.engine = db_connector.connect_db()
        else:
            self.engine = engine
        self.team_id_dict = defaultdict(lambda: "Undefined")

    def execute(self, sql, params=None):
        """
        Execute SQL statement or text. Prefer typed Core/ORM methods where possible.
        """
        stmt = text(sql) if isinstance(sql, str) else sql
        with self.engine.begin() as connection:
            out = connection.execute(stmt, params or {})
        return out

    def get_team_id(self, id_dict, team_abbrev):
        """
        Get team ID from db if it exists and store in dictionary if not
        """
        if id_dict[team_abbrev] == "Undefined":
            stmt = select(Teams.id).where(Teams.nameAbbrev == team_abbrev)
            with self.engine.connect() as connection:
                res = connection.execute(stmt).first()
            if res:
                team_id = res[0]
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
        with self.engine.connect() as connection:
            stmt = select(Games.apiID, Games.outcome).where(Games.apiID == game.api_id)
            query_res = connection.execute(stmt).first()
        return query_res

    def check_season_exists(self, season_api_id):
        """
        Check if season exists in db
        """
        with self.engine.connect() as connection:
            stmt = select(Seasons.apiID).where(Seasons.apiID == season_api_id)
            query_res = connection.execute(stmt).first()
        return query_res

    def check_team_exists(self, team_abbrev):
        """
        Check if team exists in db
        """
        with self.engine.connect() as connection:
            stmt = select(Teams.nameAbbrev).where(Teams.nameAbbrev == team_abbrev)
            query_res = connection.execute(stmt).first()
        return query_res

    def ensure_season(self, season_api_id: str) -> None:
        int_api_id = int(season_api_id)
        start_year = int_api_id // 10000
        end_year = int_api_id % 10000
        with self.engine.begin() as connection:
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(Seasons).values(
                            apiID=season_api_id, startYear=start_year, endYear=end_year
                        )
                    )
            except IntegrityError as e:
                logger.debug(
                    f"IntegrityError when inserting season {season_api_id}: {e}"
                )
                # season already exists (or other constraint violation)
                # We only want to ignore the "already exists" case.
                # If season_code is the only unique constraint here, it's fine to ignore.
                pass

    def ensure_team(self, abbrev: str) -> None:
        with self.engine.begin() as connection:
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(Teams).values(
                            name="Unknown",
                            nameAbbrev=abbrev,
                            conferenceAbbrev="Unknown",
                            divisionAbbrev="Unknown",
                        )
                    )
            except IntegrityError as e:
                logger.debug(f"IntegrityError when inserting team {abbrev}: {e}")
                # team already exists (or other constraint violation)
                # We only want to ignore the "already exists" case.
                # If season_code is the only unique constraint here, it's fine to ignore.
                pass

    def insert_game(self, game):
        """
        Insert game into db
        """
        date_played = getattr(game, "date_played")
        date_played = date_str_to_py(date_played)

        time_played = getattr(game, "time_played")
        time_played = datetime.strptime(time_played, "%H:%M:%S").time()

        season_api_id = getattr(game, "season_id")
        home_abbrev = getattr(game, "home_abbrev")
        away_abbrev = getattr(game, "away_abbrev")

        self.ensure_season(season_api_id)
        self.ensure_team(home_abbrev)
        self.ensure_team(away_abbrev)

        outcome = getattr(game, "outcome")
        in_ot = getattr(game, "in_ot")

        with self.engine.begin() as connection:
            season_id = (
                select(Seasons.id)
                .where(Seasons.apiID == season_api_id)
                .scalar_subquery()
            )
            home_team_id = (
                select(Teams.id)
                .where(Teams.nameAbbrev == home_abbrev)
                .scalar_subquery()
            )
            away_team_id = (
                select(Teams.id)
                .where(Teams.nameAbbrev == away_abbrev)
                .scalar_subquery()
            )

            home_points_awarded = (
                (2 if outcome == 1 else (1 if in_ot else 0)) if outcome is not None else None
            )
            away_points_awarded = (
                (2 if outcome == 0 else (1 if in_ot else 0)) if outcome is not None else None
            )

            logger.debug(f"About to insert game {game}")
            stmt = insert(Games).values(
                apiID=game.api_id,
                seasonID=season_id,
                homeTeamID=home_team_id,
                awayTeamID=away_team_id,
                datePlayed=date_played,
                dayOfYrPlayed=getattr(game, "day_of_year_played"),
                yrPlayed=getattr(game, "year_played"),
                timePlayed=time_played,
                homeTeamGoals=getattr(game, "home_team_goals"),
                awayTeamGoals=getattr(game, "away_team_goals"),
                gameTypeID=getattr(game, "game_type"),
                lastPeriodTypeID=getattr(game, "last_period_type"),
                outcome=outcome,
                inOT=in_ot,
                homeTeamPointsAwarded=home_points_awarded,
                awayTeamPointsAwarded=away_points_awarded,
                recordCreated=today_date,
            )
            logging.debug(f"Inserting game: {repr(game)}")
            connection.execute(stmt)

    def update_game(self, game):
        """
        Update game in db
        """
        stmt = (
            update(Games)
            .where(Games.apiID == game.api_id)
            .values(
                homeTeamGoals=game.home_team_goals,
                awayTeamGoals=game.away_team_goals,
                outcome=game.outcome,
                inOT=game.in_ot,
                lastPeriodTypeID=game.last_period_type_id,
            )
        )
        with self.engine.begin() as connection:
            connection.execute(stmt)

    def load_games_to_db(self, txt_path=None, overwrite=False):
        """
        Load games from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/games.txt"
        with open(txt_path, "r") as f:
            for line in f.readlines():
                game = Game.from_csv_line(line)
                exists_out = self.check_game_exists(game)
                if not exists_out:
                    self.insert_game(game)
                else:
                    api_id, outcome = exists_out
                    if outcome is None or overwrite:
                        self.update_game(game)
                    else:
                        logger.debug(
                            f"Game with ID {api_id} already exists in db with outcome {outcome}, skipping"
                        )

        txt_path = f"{self.txt_dir}/games_today.txt"
        with open(txt_path, "r") as f:
            for line in f.readlines():
                game = Game.from_csv_line(line)
                exists_out = self.check_game_exists(game)
                if not exists_out:
                    self.insert_game(game)
                else:
                    api_id, outcome = exists_out
                    logger.debug(
                        f"Game with ID {api_id} already exists in db with outcome {outcome}, skipping"
                    )

        txt_path = f"{self.txt_dir}/games_all.txt"
        with open(txt_path, "r") as f:
            for line in f.readlines():
                game = Game.from_csv_line(line)
                exists_out = self.check_game_exists(game)
                if not exists_out:
                    self.insert_game(game)
                else:
                    api_id, outcome = exists_out
                    logger.debug(
                        f"Game with ID {api_id} already exists in db with outcome {outcome}, skipping"
                    )

    def load_players(self, txt_path=None):
        """
        Load players from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/players.txt"
        with open(txt_path) as f, self.engine.begin() as connection:
            for line in f.readlines():
                api_id, full_name, first_name, last_name, number, position = (
                    split_csv_line(line)
                )
                stmt = insert(Players).values(
                    apiID=api_id,
                    name=full_name,
                    firstName=first_name,
                    lastName=last_name,
                    number=number,
                    position=position,
                )
                # sql = f'''INSERT INTO players(apiID, name, firstName, lastName, number, position)
                #        VALUES("{api_id}", "{full_name}", "{first_name}", "{last_name}", "{number}", "{position}")'''
                connection.execute(stmt)

    def load_roster_entries(self, txt_path=None):
        """
        Load roster entries (player + team + season) from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/rosterEntries.txt"
        with open(txt_path, "r") as f, self.engine.begin() as connection:
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

                team_id_stmt = select(Teams.id).where(Teams.nameAbbrev == team_abbrev)
                team_id_res = connection.execute(team_id_stmt).first()
                if not team_id_res:
                    print(f"No team found with name {team_abbrev}, skipping record")
                    continue
                team_id = team_id_res[0]

                player_id_stmt = select(Players.id).where(
                    Players.firstName == first_name, Players.lastName == last_name
                )
                player_id_res = connection.execute(player_id_stmt).first()
                if not player_id_res:
                    print(
                        f"No player found with name {first_name} {last_name}, skipping record"
                    )
                    continue
                player_id = player_id_res[0]

                insert_stmt = insert(RosterEntries).values(
                    apiID=api_id,
                    playerID=player_id,
                    teamID=team_id,
                    seasonID=year,
                    startYear=start_year,
                    endYear=end_year,
                )
                connection.execute(insert_stmt)

    def load_teams(self, txt_path=None):
        """
        Load teams from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/teams.txt"
        with open(txt_path, "r") as f, self.engine.begin() as connection:
            for line in f.readlines():
                team_name, name_abbrev, conf_abbrev, div_abbrev = split_csv_line(line)
                exists_out = self.check_team_exists(name_abbrev)
                if not exists_out:
                    connection.execute(
                        insert(Teams).values(
                            name=team_name,
                            nameAbbrev=name_abbrev,
                            conferenceAbbrev=conf_abbrev,
                            divisionAbbrev=div_abbrev,
                        )
                    )

    def load_seasons(self, txt_path=None):
        """
        Load seasons from txt to db
        """
        if not txt_path:
            txt_path = f"{self.txt_dir}/seasons.txt"
        with open(txt_path, "r") as f, self.engine.begin() as connection:
            for line in f.readlines():
                api_id, start_year, end_year = split_csv_line(line)
                exists_out = self.check_season_exists(api_id)
                if not exists_out:
                    connection.execute(
                        insert(Seasons).values(
                            apiID=api_id, startYear=start_year, endYear=end_year
                        )
                    )

    def query(self, sql, params=None):
        """
        Query the database with the given SQL statement or selectable.

        :param sql: SQL string, SQLAlchemy text(), or SQLAlchemy selectable
        :param params: optional dict of parameters
        :return: DataFrame with queried data
        """
        logger.debug(f"About to query: {sql}")
        logger.debug(f"engine: {self.engine}")
        df = pd.read_sql(sql, self.engine, params=params)
        return df

    def query_games(self, start_date=None, end_date=today_date):
        """
        Export games information with recency selection
        """
        select_stmt = games_select(start_date, end_date)
        logger.debug(select_stmt)
        with self.engine.connect() as connection:
            games = connection.execute(select_stmt).fetchall()
        return games

    def query_games_with_predictions(self, start_date, end_date=None):
        """
        Export games with predictions information with recency selection. Consumed by FastAPI endpoint.
        """
        if end_date is None:
            end_date = start_date
        select_stmt = games_with_predictions_select(start_date, end_date)
        logger.debug(select_stmt)
        with self.engine.connect() as connection:
            games_with_preds = connection.execute(select_stmt).fetchall()
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
        prediction_bin = int(prediction > 0.5)
        values = {
            "gameID": game_id,
            "predicterID": predicter_id,
            "prediction": prediction,
            "predictionBinary": prediction_bin,
            "predictionDate": today_date,
        }
        upsert(
            self.engine, GamePredictions.__table__, values, ["gameID", "predicterID"]
        )

    def add_predicter_to_register(
        self, name, predicter_class_name, path="", trainable=False, active=True
    ):
        """
        Register a new predicter in the predicterRegister table
        """
        values = {
            "predicterName": name,
            "predicterType": predicter_class_name,
            "predicterPath": path,
            "trainable": int(trainable),
            "active": int(active),
        }
        upsert(self.engine, PredicterRegister.__table__, values, ["predicterName"])

    def predicter_id_from_name(self, predicter_name):
        stmt = select(PredicterRegister.id).where(
            PredicterRegister.predicterName == predicter_name
        )
        with self.engine.connect() as connection:
            res = connection.execute(stmt).first()
        if not res:
            raise ValueError(
                f"Could not retrieve new predicter ID from predicterRegister with name {predicter_name}"
            )
        predicter_id = res[0]
        return predicter_id

    def add_predicter_to_last_training(self, predicter_id):
        values = {"predicterID": predicter_id, "lastTrainingDate": None}
        upsert(self.engine, LastTraining.__table__, values, ["predicterID"])

    # def set_action_date(self, table_name, column_name, update_date=today_date):
    #    """
    #    Set the date in a table tracking last action taken. Only allowed tables/columns are permitted.
    #    """
    #    if table_name not in _ALLOWED_ACTION_TABLE_COLUMNS or column_name not in _ALLOWED_ACTION_TABLE_COLUMNS[table_name]:
    #        raise ValueError("Invalid table_name or column_name for action date")
    #    delete_sql = text(f'DELETE FROM "{table_name}"')
    #    delete_stmt = (delete(table_name))
    #    insert_sql = text(f'INSERT INTO "{table_name}"("{column_name}") VALUES (:update_date)')
    #    insert_stmt = (insert(table_name).values({column_name: update_date}))
    #    with self.engine.begin() as conn:
    #        conn.execute(delete_sql)
    #        conn.execute(insert_sql, {"update_date": update_date})

    # def get_action_date(self, table_name, column_name):
    #    """
    #    Read the action date from a table (validated).
    #    """
    #    if table_name not in _ALLOWED_ACTION_TABLE_COLUMNS or column_name not in _ALLOWED_ACTION_TABLE_COLUMNS[table_name]:
    #        raise ValueError("Invalid table_name or column_name for action date")
    #    select_sql = text(f'SELECT "{column_name}" FROM "{table_name}" LIMIT 1')
    #    with self.engine.connect() as conn:
    #        res = conn.execute(select_sql).first()
    #    if res:
    #        return res[0]
    #    return None

    # def set_game_export_date(self):
    #    """
    #    Update the date in gamesLastExport with current date
    #    """
    #    self.set_action_date("gamesLastExport", "lastExportDate")

    # def get_game_export_date(self):
    #    """
    #    Read the date in gamesLastExport
    #    """
    #    out = self.get_action_date("gamesLastExport", "lastExportDate")
    #    return out

    def set_last_training_date(self, predicter_id):
        """
        Update the date in lastTraining with current date
        """
        values = {"predicterID": predicter_id, "lastTrainingDate": today_date}
        upsert(self.engine, LastTraining.__table__, values, ["predicterID"])

    def get_last_training_date(self, predicter_id):
        """
        Read the date in lastTraining
        """
        stmt = select(LastTraining.lastTrainingDate).where(
            LastTraining.predicterID == predicter_id
        )
        with self.engine.connect() as connection:
            res = connection.execute(stmt).first()
        return res[0] if res else None

    def get_last_prediction_date(self, predicter_id):
        """
        Read the date of the latest prediction for a predicter
        """
        stmt = select(func.max(GamePredictions.predictionDate)).where(
            GamePredictions.predicterID == predicter_id
        )
        with self.engine.connect() as connection:
            res = connection.execute(stmt).scalar()
        return res

    def get_predicters(self):
        """
        Get the predicters from the db
        """
        stmt = select(
            PredicterRegister.id,
            PredicterRegister.predicterName,
            PredicterRegister.predicterType,
            PredicterRegister.predicterPath,
            PredicterRegister.trainable,
            PredicterRegister.active,
        )
        with self.engine.connect() as connection:
            rows = connection.execute(stmt).fetchall()
        out = [list(row) for row in rows]
        return out
