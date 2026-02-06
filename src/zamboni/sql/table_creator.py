import logging
from sqlalchemy import text
from .tables import Base, table_classes, view_classes
from .view_statements import create_view_statement, drop_view_statement

logger = logging.getLogger(__name__)


class TableCreator:
    """Class to create tables in SQLite db"""

    def __init__(self, con):
        """
        Store connection variable

        :param con: SQLite db connector
        """
        self.con = con

    def get_existing_class_names(self):
        return Base.metadata.tables.keys()

    def existing_view_names(self):
        existing_class_names = self.get_existing_class_names()
        existing_view_names = [
            class_name
            for class_name in existing_class_names
            if class_name in view_classes
        ]
        view_names = [
            view_classes[class_name].__tablename__ for class_name in existing_view_names
        ]
        return view_names

    def drop_view(self, view_name):
        drop_statement = drop_view_statement.format(view_name=view_name)
        with self.con.begin() as connection:
            connection.execute(text(drop_statement))

    def create_view(self, view_name):
        create_statement = create_view_statement(view_name, self.con.dialect.name)
        with self.con.begin() as connection:
            connection.execute(text(create_statement))

    def drop_all(self, table_list=None):
        view_names = list(view_classes.keys())
        # Need to delete in opposite order to creation due to dependencies
        reversed_names = view_names[::-1]
        for view_name in reversed_names:
            logging.info(f"Dropping view {view_name}")
            self.drop_view(view_name)
        logging.info("Dropping tables")
        Base.metadata.drop_all(self.con, tables=table_list)

    def create_tables(self, table_list=None, overwrite=False):
        if table_list is None:
            table_list = list(table_classes.values())
        else:
            table_list = [table_classes[table_name] for table_name in table_list]
        table_list = [table.__table__ for table in table_list]
        if overwrite:
            self.drop_all(table_list=table_list)
        logging.info("Creating tables")
        Base.metadata.create_all(self.con, tables=table_list)
        for view_name in view_classes.keys():
            logging.info(f"Creating view {view_name}")
            self.create_view(view_name)

    # def create_table(self, table_name, recreate=False, is_view=False):
    #    """
    #    Connect to db and create table

    #    :param statement: SQL expression creating table
    #    """
    #    logger.info(f"Creating table {table_name}")
    #    if is_view:
    #        drop_statement = drop_view_statement
    #        drop_statement = drop_statement.format(view_name=table_name)
    #        create_statements = create_view_statements
    #    else:
    #        drop_statement = drop_table_statement
    #        drop_statement = drop_statement.format(table_name=table_name)
    #        create_statements = create_table_statements

    #    with self.con as cursor:
    #        if recreate:
    #            cursor.execute(drop_statement)
    #        create_statement = create_statements[table_name]
    #        cursor.execute(create_statement)
    #        cursor.commit()
