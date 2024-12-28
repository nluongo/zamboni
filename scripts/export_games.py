import pandas as pd
from zamboni import DBConnector, Exporter
from zamboni.export_statements import export_statements

export_sql = export_statements['games']

db_con = DBConnector('data/zamboni.db')
conn = db_con.connect_db()

exporter = Exporter(conn)
exporter.export(export_sql, 'data/games.parquet')

