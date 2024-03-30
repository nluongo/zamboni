import sqlite3
import logging
from pathlib import Path

class DBConnector():
    def __init__(self, db_path='data/zamboni.db'):
        self.db_path = Path(db_path)

    def connect_db(self):
        if self.db_path.is_file():
            logging.info(f'Opening existing DB at {self.db_path}')
        else:
            logging.info(f'Creating new DB at {self.db_path}')
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def get_cursor(self):
        if not self.conn:
            self.connect_db()
        cursor = self.conn.cursor()
        return cursor

    def close(self):
        self.con.close()
