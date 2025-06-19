from zamboni import DBConnector, Exporter

db_con = DBConnector("data/zamboni.db")
conn = db_con.connect_db()

exporter = Exporter(conn)
exporter.export_games(dest="data/games_all.parquet")
