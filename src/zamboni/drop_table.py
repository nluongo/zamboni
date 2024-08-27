from zamboni.db_con import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

sql = f'''DROP TABLE teams'''
cursor.execute(sql)
conn.commit()
