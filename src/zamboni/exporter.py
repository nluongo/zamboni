import os
import pandas as pd
import requests
from .db_con import DBConnector 
from .sql.export_statements import export_statements

class Exporter():
    """ Class for exporting data from database to file for training """
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self, con=None):
        """
        Initialize Exporter

        :param conn: Connecti
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
        df.to_parquet(dest)

    def games_export(self, dest='data/games.parquet', after_date=None):
        """
        Export games information with recency selection
        """
        export_sql = self.export_statements['games']
        # If after_date given, filter for only games after this date
        if after_date:
            export_sql += f'WHERE games.datePlayed >= "{after_date}"' 
        print(export_sql)
        if os.path.exists(dest):
            raise ValueError("Exported file exists, which could be a sign that training was not performed. Refusing to overwrite and exiting.")
            return
        self.export(export_sql, dest)

