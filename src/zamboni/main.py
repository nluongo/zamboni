import argparse
import logging
from zamboni.api_download import main as download_main
from zamboni import SQLLoader, Exporter, DBConnector, TableCreator
from zamboni.trainer import Trainer, ModelInitializer,TrainingDataLoader

def main():
    parser = argparse.ArgumentParser(description='Process NHL data pipeline.')

    # Flag to control downloading NHL data.
    parser.add_argument('--download', action='store_true', help='Download NHL data')
    parser.add_argument('--no-download', dest='download', action='store_false', help='Skip downloading NHL data')
    parser.set_defaults(download=True)

    # Flag to control creating tables in the database.
    parser.add_argument('--create_tables', action='store_true', help='Create database tables')
    parser.add_argument('--no-create-tables', dest='create_tables', action='store_false', help='Skip creating tables')
    parser.set_defaults(create_tables=False)

    # Flag to delete and recreate all tables and views
    parser.add_argument('--force-recreate-tables', dest='force_recreate_tables', action='store_true', help='Force deletion and re-creation of all tables and views')

    # Flag to control loading data into the database.
    parser.add_argument('--load-db', action='store_true', help='Load data into the database')
    parser.add_argument('--no-load-db', dest='load_db', action='store_false', help='Skip loading data into the database')
    parser.set_defaults(load_db=True)

    # Flag to control exporting the data.
    parser.add_argument('--export', action='store_true', help='Export data')
    parser.add_argument('--no-export', dest='export', action='store_false', help='Skip data export')
    parser.set_defaults(export=True)

    # Flag to control training the model.
    parser.add_argument('--train', action='store_true', help='Train the model')
    parser.add_argument('--no-train', dest='train', action='store_false', help='Skip training the model')
    parser.set_defaults(train=True)

    args = parser.parse_args()
    download=args.download
    create_tables = args.create_tables
    load_db = args.load_db
    export = args.export
    train = args.train

    if download:
        download_main()

    if create_tables or load_db or export:
        db_connector = DBConnector()
        db_con = db_connector.connect_db()
    
    if create_tables:
        table_creator = TableCreator(db_con)
        table_creator.create_table('teams', recreate=force_recreate_tables)
        table_creator.create_table('games', recreate=force_recreate_tables)
        table_creator.create_table('gamesLastExport', recreate=force_recreate_tables)
        table_creator.create_table('games_history', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_per_team', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_prev_same_opp', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_with_previous', is_view=True, recreate=force_recreate_tables)
        #table_creator.create_table('rosterEntries')

    loader=None
    if load_db:
        loader = SQLLoader(db_con=db_con)
        loader.load_teams()
        #loader.load_players()
        #loader.load_roster_entries()
        loader.load_games()
    
    if export:
        # Export all or only new games
        exporter = Exporter(con=db_con)
        last_export_date = exporter.last_game_export()
        exporter.games_export(dest='data/games.parquet', after_date=last_export_date)
        if not loader:
            loader = SQLLoader(db_con=db_con)
        loader.set_game_export_date()

    if train:
        # Train NN from scratch or only using new data
        nn_loader = TrainingDataLoader('data/games.parquet')
        nn_loader.load_parquet()
        nn_loader.define_columns()
        nn_loader.split_data()
        nn_loader.scale_data()
        nn_loader.create_datasets()
        nn_loader.create_dataloaders()

        model_init = ModelInitializer('data/embed_nn', 'EmbeddingNN', nn_loader.data)
        model, optimizer, epoch, loss = model_init.get_model()
        trainer = Trainer(model, optimizer, nn_loader.train_loader, nn_loader.test_loader)
        trainer.train()

        model_init.save_model('embed_nn', trainer.end_epoch, trainer.end_loss)

if __name__ == '__main__':
    main()
