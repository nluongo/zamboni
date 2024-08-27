from zamboni.db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

with open('data/teams.txt') as f:
    for line in f.readlines():
        split_line = line.split(',')
        split_line = [entry.strip() for entry in split_line]
        team_name, name_abbrev, conf_abbrev, div_abbrev = split_line
        sql = f'''INSERT INTO teams(name, nameAbbrev, conferenceAbbrev, divisionAbbrev)
                VALUES("{team_name}", "{name_abbrev}", "{conf_abbrev}", "{div_abbrev}")'''
        cursor.execute(sql)
        conn.commit()
