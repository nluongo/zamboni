import requests
import pandas as pd
from .db_con import DBConnector 

class Exporter():
    """ Class for exporting data from database to file for training """
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self, db_connector=None):
        """
        Initialize Exporter

        :param conn: Connection object for SQL db
        """
        if not db_connector:
            self.db_connector = DBConnector()
        else:
            self.db_connector = db_connector

    def export(self, sql, dest):
        """
        Export the data returned by sql to the given destination

        :param sql: SQL statement to query information from db
        :param dest: Path to export data
        """
        df = pd.read_sql(sql, self.db_connector.conn)
        df.to_parquet(dest)
