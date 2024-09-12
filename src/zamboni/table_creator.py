class TableCreator():
    ''' Class to create tables in SQLite db '''

    def __init__(self, con):
        '''
        Store connection variable

        :param con: SQLite db connector
        '''
        self.con = con

    def create_table(self, statement):
        '''
        Connect to db and create table

        :param statement: SQL expression creating table
        '''
        with self.con as cursor:
            cursor.execute(statement)
            cursor.commit()
        
