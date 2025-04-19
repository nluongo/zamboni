import logging
import os
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted
from zamboni.api_download import main as download_main
from zamboni import SQLLoader, Exporter, DBConnector, TableCreator
from zamboni.data_management import ZamboniDataManager, ZamboniData, ColumnTracker
from zamboni.training import Trainer, ModelInitializer
from zamboni.sport import TeamService

logger = logging.getLogger(__name__)

def run(download=True, create_tables=False, force_recreate_tables=False, load_db=True, export=True, report=True, train=True):
    if download:
        download_main()

    db_connector = DBConnector()
    db_con = db_connector.connect_db()
    loader = SQLLoader(db_con=db_con)
    
    if load_db or report:
        team_service = TeamService(db_con)
        team_service.build_abbrev_id_dicts()

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
        loader.load_games(team_service)
        #loader.load_players()
        #loader.load_roster_entries()
    
    training_data_path = 'data/games.parquet'
    todays_data_path = 'data/todays_games.parquet'

    if export:
        # Export all or only new games
        exporter = Exporter(con=db_con)
        last_training_date = loader.get_last_training_date()
        exporter.export_todays_games(dest=todays_data_path)
        exporter.export_games(dest=training_data_path, after_date=last_training_date)
        loader.set_game_export_date()
    print('Done exporting')

    model_init = None
    trainer = None
    if train:
        # Train NN from scratch or only using new data
        data_manager = ZamboniDataManager(training_data_path)
        data_manager.load_parquet()
        num_samples = data_manager.num_samples()
        if num_samples == 0:
            logging.info('No samples in games.parquet, exiting...')
            return
        data_manager.split_data()

        if model_init is None:
            column_tracker = ColumnTracker(data_manager.data.columns.tolist())
            model_init = ModelInitializer('data/embed_nn', 'EmbeddingNN', column_tracker)
            model, optimizer, scaler, _, _ = model_init.get_model()
            trainer = Trainer(model, optimizer)

        train_data = ZamboniData(data_manager.train_data, column_tracker=column_tracker)
        test_data = ZamboniData(data_manager.test_data, column_tracker=column_tracker)

        train_data.prep_data(scaler=scaler, fit=True)
        test_data.prep_data(scaler=scaler)

        trainer.train(train_data.loader, test_data.loader)

        model_init.save_model('data/embed_nn', trainer.end_epoch, trainer.end_loss)
        if not loader:
            loader = SQLLoader(db_con=db_con)
        loader.set_last_training_date()

        os.remove(training_data_path)

    if report:
        print('In reporting')
        reporting_data_manager = ZamboniDataManager(todays_data_path)
        reporting_data_manager.load_parquet()
        num_samples = reporting_data_manager.num_samples()
        if num_samples == 0:
            logging.info('No samples in todays_games.parquet, exiting...')
        else:
            column_tracker = ColumnTracker(reporting_data_manager.data.columns.tolist())
            model_init = ModelInitializer('data/embed_nn', 'EmbeddingNN', column_tracker)
            model, optimizer, scaler, _, _ = model_init.get_model()
            trainer = Trainer(model, optimizer)

            todays_data = ZamboniData(reporting_data_manager.data, column_tracker=column_tracker)
            # If scaler not fitted, fit as this is a new model and not loaded
            if hasattr(scaler, "n_features_in_"):
                todays_data.prep_data(scaler=scaler)
            else:
                todays_data.prep_data(scaler=scaler, fit=True)

            _, preds, _ = trainer.eval(todays_data.loader)
            data_with_preds = reporting_data_manager.data.copy()
            data_with_preds['preds'] = preds
            
            for row in data_with_preds.itertuples():
                home_abbrev = team_service.abbrev_from_id(row.homeTeamID)
                away_abbrev = team_service.abbrev_from_id(row.awayTeamID)
                if row.preds > 0.5:
                    pred_winner = home_abbrev
                else:
                    pred_winner = away_abbrev
                print(f'Game: {home_abbrev} vs {away_abbrev} on {row.datePlayed}')
                print(f'Predicted winner: {pred_winner}')
                print('---')
