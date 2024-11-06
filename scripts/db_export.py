import pandas as pd
from zamboni import DBConnector, Exporter

db_con = DBConnector('data/zamboni.db')
conn = db_con.connect_db()

exporter = Exporter(conn)
exporter.export("SELECT homeTeamID, awayTeamID, dayOfYrPlayed, yrPlayed, outcome FROM games", 'data/games.parquet')

