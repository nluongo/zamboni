from zamboni import create_statements, DBConnector, TableCreator

game_table_statement = create_statements['games']

dbcon = DBConnector('data/zamboni.db')
con = dbcon.connect_db()
tabler = TableCreator(con)
tabler.create_table(game_table_statement)

con.close()

