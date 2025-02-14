from zamboni.api_download import main as download_main
from zamboni import SQLLoader, Exporter, DBConnector, TableCreator
from zamboni.export_statements import export_statements
from zamboni.db_con import DBConnector

def main():

    download_main()

    db_connector = DBConnector()
    db_con = db_connector.connect_db()
    
    table_creator = TableCreator(db_con)
    table_creator.create_table('teams')
    table_creator.create_table('games')
    #table_creator.create_table('rosterEntries')

    loader = SQLLoader(db_con=db_con)
    loader.load_teams()
    #loader.load_players()
    #loader.load_roster_entries()
    loader.load_games()
    
    #exporter = Exporter(db_connector=db_connector)
    #export_sql = export_statements['games']
    #exporter.export(export_sql, 'data/games.parquet')

if __name__ == '__main__':
    main()
