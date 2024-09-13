import requests
import pandas as pd
from .db_con import DBConnector 

class Exporter():
    """ Class for exporting data from database to file for training """
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self, conn):
        """
        Initialize Exporter

        :param conn: Connection object for SQL db
        """
        self.conn = conn

    def export(self, sql, dest):
        """
        Export the data returned by sql to the given destination

        :param sql: SQL statement to query informaiont from db
        :param dest: Path to export data
        """
        df = pd.read_sql(sql, self.conn)
        df.to_parquet(dest)
