from zamboni import DBConnector, TableCreator

db_connector = DBConnector()
db_con = db_connector.connect_db()

table_creator = TableCreator(db_con)
table_creator.create_table("gamePredictions", recreate=True)
