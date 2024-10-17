from zamboni import DBConnector

db = DBConnector()
conn = db.connect_db()
cursor = conn.cursor()

sql = '''DROP TABLE games'''
cursor.execute(sql)
conn.commit()
