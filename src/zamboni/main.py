from zamboni.api_download import main as download_main
from zamboni.sql_loader import SQLLoader
from zamboni.exporter import Exporter
from zamboni.export_statements import export_statements
from zamboni.db_con import DBConnector

download_main()

db_connector = DBConnector()

loader = SQLLoader(db_connector=db_connector)
loader.load_teams()
#loader.load_players()
#loader.load_roster_entries()
loader.load_games()

#exporter = Exporter(db_connector=db_connector)
#export_sql = export_statements['games']
#exporter.export(export_sql, 'data/games.parquet')
