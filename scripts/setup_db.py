from zamboni import DBConnector, TableCreator
import logging

logging.basicConfig(level='INFO')

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
    table_creator.create_table(table_name)

for view_name in view_names:
    table_creator.create_table(view_name, is_view=True)

con.close()

