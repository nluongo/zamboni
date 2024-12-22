from zamboni import SQLLoader

loader = SQLLoader()
loader.load_teams()
loader.load_players()
loader.load_roster_entries()
loader.load_games()
