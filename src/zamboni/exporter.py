import logging
import pandas as pd
from .db_con import DBConnector
from zamboni.sql.sql_handler import SQLHandler
from zamboni.sql.export_statements import export_statements
from zamboni.utils import get_today_date, get_tomorrow_date

logger = logging.getLogger(__name__)
today_date = str(get_today_date())


class Exporter:
    """Class for exporting data from database to file for training"""

    def __init__(self, con=None):
        """
        Initialize Exporter

        :param conn: Connection
        """
        self.sql_handler = SQLHandler()
        if not con:
            self.db_connector = DBConnector()
            self.con = self.db_connector.connect_db()
        else:
            self.con = con
        self.export_statements = export_statements

    def last_game_export(self):
        """
        Get the last date for which games were exported
        """
        last_game_sql = self.export_statements["games_last_export"]

        df = pd.read_sql(last_game_sql, self.con)
        last_export_col = df["lastExportDate"]
        if len(last_export_col) == 0:
            out = None
        elif len(last_export_col) == 1:
            out = last_export_col[0]
        else:
            raise ValueError("Multiple rows found in gamesLastExport")
        return out

    def export(self, df, dest):
        """
        Export the data returned by sql to the given destination

        :param sql: SQL statement to query information from db
        :param dest: Path to export data
        """
        if df is not None:
            df.to_parquet(dest)
        else:
            logger.info("Nothing to export")

    def export_games(
        self, dest="data/games.parquet", after_date=None, before_date=today_date
    ):
        """
        Export games information with recency selection
        :param dest: Path to export data
        :param after_date: Date to filter games after
        :param before_date: Date to filter games before
        """
        games = self.sql_handler.query_games(
            after_date=after_date, before_date=before_date
        )
        self.export(games, dest)

    def export_todays_games(self, dest="data/todays_games.parquet"):
        """
        Export today's games

        :param dest: Path to export data
        """
        tomorrow_date = str(get_tomorrow_date())
        self.export_games(dest=dest, after_date=today_date, before_date=tomorrow_date)
