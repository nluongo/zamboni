from sqlalchemy import create_engine

# import sqlite3
import logging

logger = logging.getLogger(__name__)


class DBConnector:
    """Get connection to SQLite db"""

    def __init__(self, db_uri):
        """
        Store path to db

        :param db_path: Path to db
        """
        self.db_uri = db_uri

    def connect_db(self):
        """
        Connect to db or create if it doesn't exist
        """
        engine = create_engine(self.db_uri)
        # if self.db_path.is_file():
        #    logger.info(f"Opening existing DB at {self.db_path}")
        # else:
        #    logger.info(f"Creating new DB at {self.db_path}")
        #    os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # self.conn = sqlite3.connect(self.db_path)
        # self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return engine

    def close(self):
        """
        Close connection
        """
        self.conn.close()
