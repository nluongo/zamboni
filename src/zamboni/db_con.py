import sqlite3
import logging
from pathlib import Path

class DBConnector():
    def __init__(self, db_path):
        self.db_path = Path(db_path)

    def connect_db(self):
        if self.db_path.is_file():
            logging.info(f'Opening existing DB at {self.db_path}')
        else:
            logging.info(f'Creating new DB at {self.db_path}')
        self.con = sqlite3.connect(self.db_path)
        return self.con

    def close(self):
        self.con.close()
