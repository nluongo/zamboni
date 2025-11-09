import logging
from .table_statements import create_table_statements, drop_table_statement
from .view_statements import create_view_statements, drop_view_statement

logger = logging.getLogger(__name__)


class TableCreator:
    """Class to create tables in SQLite db"""

    def __init__(self, con):
        """
        Store connection variable

        :param con: SQLite db connector
        """
        self.con = con

    def create_table(self, table_name, recreate=False, is_view=False):
        """
        Connect to db and create table

        :param statement: SQL expression creating table
        """
        logger.info(f"Creating table {table_name}")
        if is_view:
            drop_statement = drop_view_statement
            drop_statement = drop_statement.format(view_name=table_name)
            create_statements = create_view_statements
        else:
            drop_statement = drop_table_statement
            drop_statement = drop_statement.format(table_name=table_name)
            create_statements = create_table_statements

        with self.con as cursor:
            if recreate:
                cursor.execute(drop_statement)
            create_statement = create_statements[table_name]
            cursor.execute(create_statement)
            cursor.commit()
