import logging
import os
import pandas as pd
import requests
from .db_con import DBConnector 
from .sql.export_statements import export_statements
from zamboni.utils import get_today_date, get_tomorrow_date

logger = logging.getLogger(__name__)
today_date = str(get_today_date())

class Exporter():
    """ Class for exporting data from database to file for training """

    def __init__(self, con=None):
        """
        Initialize Exporter

        :param conn: Connection
        """
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
        last_game_sql = self.export_statements['games_last_export']

        df = pd.read_sql(last_game_sql, self.con)
        last_export_col = df['lastExportDate']
        if len(last_export_col) == 0:
            out = None
        elif len(last_export_col) == 1:
            out = last_export_col[0]
        else:
            raise ValueError('Multiple rows found in gamesLastExport')
        return out

    def export(self, sql, dest):
        """
        Export the data returned by sql to the given destination

        :param sql: SQL statement to query information from db
        :param dest: Path to export data
        """
        df = pd.read_sql(sql, self.con)
        #if len(df) == 0:
        #    logging.info('No events read for export, exiting without creating file.')
        #    return 0
        df.to_parquet(dest)
        #return 1

    def export_games(self, dest='data/games.parquet', after_date=None, before_date=today_date):
        """
        Export games information with recency selection
        """
        export_sql = self.export_statements['games']
        # If after_date given, filter for only games after this date
        if not after_date:
            export_sql += f'WHERE games.datePlayed < "{before_date}" '
        else:
            export_sql += f'WHERE games.datePlayed < "{before_date}" ' 
            export_sql += f'AND games.datePlayed >= "{after_date}" '
        logging.info(export_sql)
        self.export(export_sql, dest)

    def export_todays_games(self, dest='data/todays_games.parquet'):
        """
        Export today's games

        :param dest: Path to export data
        """
        tomorrow_date = str(get_tomorrow_date())
        self.export_games(dest=dest, after_date=today_date, before_date=tomorrow_date)
