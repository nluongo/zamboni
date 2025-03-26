import argparse
import logging
from zamboni.api_download import main as download_main
from zamboni import SQLLoader, Exporter, DBConnector, TableCreator
from zamboni.data_management import ZamboniDataManager, ZamboniData, ColumnTracker
from zamboni.training import Trainer, ModelInitializer
from sklearn.preprocessing import StandardScaler

def main():
    parser = argparse.ArgumentParser(description='Process NHL data pipeline.')

    # Flag to control downloading NHL data.
    parser.add_argument('--download', action='store_true', help='Download NHL data')
    parser.add_argument('--no-download', dest='download', action='store_false', help='Skip downloading NHL data')
    parser.set_defaults(download=True)

    # Flag to control creating tables in the database.
    parser.add_argument('--create-tables', action='store_true', help='Create database tables')
    parser.add_argument('--no-create-tables', dest='create_tables', action='store_false', help='Skip creating tables')
    parser.set_defaults(create_tables=False)

    # Flag to delete and recreate all tables and views
    parser.add_argument('--force-recreate-tables', dest='force_recreate_tables', action='store_true', help='Force deletion and re-creation of all tables and views')
    parser.set_defaults(force_recreate_tables=False)

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
    force_recreate_tables = args.force_recreate_tables

    if download:
        download_main()

    if create_tables or load_db or export:
        db_connector = DBConnector()
        db_con = db_connector.connect_db()
        loader = SQLLoader(db_con=db_con)
    
    if create_tables:
        table_creator = TableCreator(db_con)
        table_creator.create_table('teams', recreate=force_recreate_tables)
        table_creator.create_table('games', recreate=force_recreate_tables)
        table_creator.create_table('gamesLastExport', recreate=force_recreate_tables)
        table_creator.create_table('lastTraining', recreate=force_recreate_tables)
        table_creator.create_table('games_history', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_per_team', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_prev_same_opp', is_view=True, recreate=force_recreate_tables)
        table_creator.create_table('games_with_previous', is_view=True, recreate=force_recreate_tables)
        #table_creator.create_table('rosterEntries')

    if load_db:
        loader.load_teams()
        #loader.load_players()
        #loader.load_roster_entries()
        loader.load_games()
    
    if export:
        # Export all or only new games
        exporter = Exporter(con=db_con)
        last_training_date = loader.get_last_training_date()
        exporter.export_games(dest='data/games.parquet', after_date=last_training_date)
        loader.set_game_export_date()

    if train:
        # Train NN from scratch or only using new data


        data_manager = ZamboniDataManager('data/games.parquet')
        data_manager.load_parquet()
        data_manager.split_data()

        column_tracker = ColumnTracker(data_manager.data.columns.tolist())

        train_data = ZamboniData(data_manager.train_data, column_tracker=column_tracker)
        test_data = ZamboniData(data_manager.test_data, column_tracker=column_tracker)

        scaler=StandardScaler()

        train_data.scale_data(scaler=scaler, fit=True)
        train_data.readd_noscale_columns()
        train_data.create_dataset()
        train_data.create_dataloader()

        test_data.scale_data(scaler=scaler)
        test_data.readd_noscale_columns()
        test_data.create_dataset()
        test_data.create_dataloader()

        model_init = ModelInitializer('data/embed_nn', 'EmbeddingNN', column_tracker)
        model, optimizer, epoch, loss = model_init.get_model()
        trainer = Trainer(model, optimizer)
        trainer.train(train_data.loader, test_data.loader)

        model_init.save_model('embed_nn', trainer.end_epoch, trainer.end_loss)
        if not loader:
            loader = SQLLoader(db_con=db_con)
        loader.set_last_training_date()

if __name__ == '__main__':
    main()
