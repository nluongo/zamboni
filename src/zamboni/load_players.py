from db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

with open('data/players.txt') as f:
    for line in f.readlines():
        line = [entry.strip() for entry in line.split(',')]
        print(line)
        api_id, full_name, first_name, last_name, number, position = line
        sql = f'''INSERT INTO players(apiID, name, firstName, lastName, number, position)
                VALUES("{api_id}", "{full_name}", "{first_name}", "{last_name}", "{number}", "{position}")'''
        cursor.execute(sql)
        conn.commit()
