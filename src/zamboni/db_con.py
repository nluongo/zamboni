import sqlite3
import logging
from pathlib import Path
import os

class DBConnector():
    ''' Get connection to SQLite db '''
    def __init__(self, db_path='data/zamboni.db'):
        '''
        Store path to db

        :param db_path: Path to db
        '''
        self.db_path = Path(db_path)

    def connect_db(self):
        '''
        Connect to db or create if it doesn't exist
        '''
        if self.db_path.is_file():
            logging.info(f'Opening existing DB at {self.db_path}')
        else:
            logging.info(f'Creating new DB at {self.db_path}')
            os.makedirs(self.db_path, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def get_cursor(self):
        '''
        Get cursor for interacting with db
        '''
        if not self.conn:
            self.connect_db()
        self.cursor = self.conn.cursor()
        return self.cursor

    def close(self):
        '''
        Close connection
        '''
        self.con.close()
