class TableCreator():
    def __init__(self, con):
        self.con = con

    def create_table(self, statement):
        with self.con as cursor:
            cursor.execute(statement)
            self.con.commit()
        
