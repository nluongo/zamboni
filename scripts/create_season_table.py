from zamboni import create_statements, DBConnector, TableCreator

season_table_statement = create_statements['seasons']

dbcon = DBConnector('zamboni.db')
con = dbcon.connect_db()
tabler = TableCreator(con)
tabler.create_table(season_table_statement)

con.close()

