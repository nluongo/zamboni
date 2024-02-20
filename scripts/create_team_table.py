from zamboni import create_statements, DBConnector, TableCreator

team_table_statement = create_statements['teams']

dbcon = DBConnector('zamboni.db')
con = dbcon.connect_db()
tabler = TableCreator(con)
tabler.create_table(team_table_statement)

con.close()

