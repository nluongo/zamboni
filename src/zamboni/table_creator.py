from zamboni.table_statements import create_table_statements, drop_table_statements
from zamboni.view_statements import create_view_statements, drop_view_statements

class TableCreator():
    ''' Class to create tables in SQLite db '''

    def __init__(self, con):
        '''
        Store connection variable

        :param con: SQLite db connector
        '''
        self.con = con

    def create_table(self, table_name, recreate=True, is_view=False):
        '''
        Connect to db and create table

        :param statement: SQL expression creating table
        '''
        if is_view:
            drop_statements = drop_view_statements
            create_statements = create_view_statements
        else:
            drop_statements = drop_table_statements
            create_statements = create_table_statements
            
        with self.con as cursor:
            if recreate:
                drop_statement = drop_statements[table_name]
                cursor.execute(drop_statement)
            create_statement = create_statements[table_name]
            cursor.execute(create_statement)
            cursor.commit()
