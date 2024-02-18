from zamboni import create_statements, DBConnector, TableCreator

player_table_statement = create_statements['games']

dbcon = DBConnector('zamboni.db')
con = dbcon.connect_db()
tabler = TableCreator(con)
tabler.create_table(player_table_statement)

con.close()

