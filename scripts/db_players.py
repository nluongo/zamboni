import zamboni
import pandas as pd
from zamboni import DBConnector

db_con = DBConnector('data/zamboni.db')
conn = db_con.connect_db()
print(db_con)

df = pd.read_sql("SELECT * FROM players", conn)
print(df)

