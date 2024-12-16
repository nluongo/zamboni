from zamboni import create_statements, DBConnector, TableCreator

table_names = [
    'teams',
    'games',
    'players',
    'rosterEntries'
    ]

view_names = [
    'games_per_team',
    'games_with_previous',
    ]

dbcon = DBConnector('data/zamboni.db')
con = dbcon.connect_db()
table_creator = TableCreator(con)

for table_name in table_names:
    create_statement = create_statements[table_name]
    table_creator.create_table(create_statement)

for view_name in view_names:
    view_statement = view_statements[view_name]
    table_creator.create_table(view_statement]

con.close()

