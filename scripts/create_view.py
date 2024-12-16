from zamboni import DBConnector
#from zamboni import game_per_team_statement, games_with_previous_statement
from zamboni.view_statements import view_statements

view_statement = view_statements['games_prev_same_opp']

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

print('Running SQL:')
print(view_statement)
cursor.execute(view_statement)
conn.commit()
