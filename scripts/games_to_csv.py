from zamboni import SQLHandler

sql_handler = SQLHandler()
games_df = sql_handler.query_games()
games_csv = games_df.to_csv("data/games.csv", index=False, header=False)
