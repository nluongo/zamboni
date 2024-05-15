from .db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

with open('data/players.txt') as f:
    for line in f.readlines():
        team_name, name_abbrev, conf_abbrev, div_abbrev = line.split(',')
        print(player_name)
        sql = f'''INSERT INTO teams(name, nameAbbrev, conferenceAbbrev, divisionAbbrev)
                VALUES("{team_name}", "{name_abbrev}", "{conf_abbrev}", "{div_abbrev}")'''
        cursor.execute(sql)
        conn.commit()
