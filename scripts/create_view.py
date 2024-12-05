from zamboni import DBConnector
#from zamboni import game_per_team_statement, games_with_previous_statement
from zamboni.view_statements import games_per_team_statement, games_with_previous_statement

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

#sql = games_with_previous_statement
sql = games_per_team_statement
print(sql)
cursor.execute(sql)
conn.commit()
