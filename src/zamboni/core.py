import logging
from zamboni.api_download import main as download_main
from zamboni import SQLHandler, Exporter, DBConnector, TableCreator
from zamboni.predicter_service import PredicterService
from zamboni.data_management import ZamboniDataManager, ZamboniData, ColumnTracker
from zamboni.training import Trainer, ModelInitializer
from zamboni.sport import TeamService
from zamboni.utils import today_date_str

logger = logging.getLogger(__name__)


def run(
    download=True,
    create_tables=True,
    force_recreate_tables=False,
    load_db=True,
    export=True,
    report=True,
    train=True,
):
    if download:
        download_main()

    db_connector = DBConnector()
    db_con = db_connector.connect_db()
    sql_handler = SQLHandler(db_con=db_con)

    if report or train:
        predicters_service = PredicterService()
        predicters = predicters_service.get_predicters()

    if create_tables:
        table_creator = TableCreator(db_con)
        table_creator.create_table("teams", recreate=force_recreate_tables)
        table_creator.create_table("games", recreate=force_recreate_tables)
        table_creator.create_table("gamesLastExport", recreate=force_recreate_tables)
        table_creator.create_table("lastTraining", recreate=force_recreate_tables)
        table_creator.create_table("predicterRegister", recreate=force_recreate_tables)
        table_creator.create_table("gamePredictions", recreate=force_recreate_tables)
        table_creator.create_table(
            "games_history", is_view=True, recreate=force_recreate_tables
        )
        table_creator.create_table(
            "games_per_team", is_view=True, recreate=force_recreate_tables
        )
        table_creator.create_table(
            "games_prev_same_opp", is_view=True, recreate=force_recreate_tables
        )
        table_creator.create_table(
            "games_with_previous", is_view=True, recreate=force_recreate_tables
        )
        # table_creator.create_table('rosterEntries')

    if load_db or report:
        team_service = TeamService(db_con)

    if load_db:
        sql_handler.load_teams()
        team_service.build_abbrev_id_dicts()
        sql_handler.load_games_to_db(team_service)
        # sql_handler.load_players()
        # sql_handler.load_roster_entries()

    for predicter in predicters:
        if not predicter.active:
            continue
        logging.info(f"Initializing predicter: {predicter.name}")
        if predicter.trainable:
            last_training_date = sql_handler.get_last_training_date(predicter.id)
            logging.info(
                f"Last training date for {predicter.name}: {last_training_date}"
            )
            new_games = sql_handler.query_games(after_date=last_training_date)
        else:
            last_prediction_date = sql_handler.get_last_prediction_date(predicter.id)
            new_games = sql_handler.query_games(after_date=last_prediction_date)
        predicter.update(new_games)

    todays_games = sql_handler.query_games(after_date=today_date_str())
    if todays_games:
        for predicter in predicters:
            if not predicter.active:
                continue
            logging.info(f"Running predicter: {predicter.name}")
            for game in todays_games.itertuples():
                game_id = game.id
                prediction = predicter.predict(game)
                logging.info(f"Predicted outcome for game {game_id}: {prediction}")

    training_data_path = "data/games.parquet"
    todays_data_path = "data/todays_games.parquet"

    if export:
        # Export all or only new games
        exporter = Exporter(con=db_con)
        last_training_date = sql_handler.get_last_training_date()
        logging.info("Exporting todays games")
        exporter.export_todays_games(dest=todays_data_path)
        logging.info("Exporting training games")
        exporter.export_games(dest=training_data_path, after_date=last_training_date)
        sql_handler.set_game_export_date()

    model_init = None
    trainer = None
    if train:
        # Train NN from scratch or only using new data
        data_manager = ZamboniDataManager(training_data_path)
        data_manager.load_parquet()
        num_samples = data_manager.num_samples()
        if num_samples == 0:
            logging.info("No samples in games.parquet, exiting...")
        else:
            if model_init is None:
                column_tracker = ColumnTracker(data_manager.data.columns.tolist())
                model_init = ModelInitializer(
                    "data/embed_nn", "EmbeddingNN", column_tracker
                )
                model, optimizer, scaler, _, _ = model_init.get_model()
                trainer = Trainer(model, optimizer)

            train_data = ZamboniData(data_manager.data, column_tracker=column_tracker)
            train_data.prep_data(scaler=scaler, fit=True)

            trainer.train(train_data.loader)

            model_init.save_model("data/embed_nn", trainer.end_epoch, trainer.end_loss)
            if not sql_handler:
                sql_handler = SQLHandler(db_con=db_con)
            sql_handler.set_last_training_date()

    if report:
        report_path = f"data/predictions/preds_{today_date_str()}.txt"
        reporting_data_manager = ZamboniDataManager(todays_data_path)
        reporting_data_manager.load_parquet()
        num_samples = reporting_data_manager.num_samples()
        if num_samples == 0:
            logging.info("No samples in todays_games.parquet, exiting...")
        else:
            column_tracker = ColumnTracker(reporting_data_manager.data.columns.tolist())
            model_init = ModelInitializer(
                "data/embed_nn", "EmbeddingNN", column_tracker
            )
            model, optimizer, scaler, _, _ = model_init.get_model()
            trainer = Trainer(model, optimizer)

            todays_data = ZamboniData(
                reporting_data_manager.data, column_tracker=column_tracker
            )

            # If scaler not fitted, fit as this is a new model and not loaded
            if hasattr(scaler, "n_features_in_"):
                todays_data.prep_data(scaler=scaler)
            else:
                todays_data.prep_data(scaler=scaler, fit=True)

            _, preds, _ = trainer.eval(todays_data.loader)
            data_with_preds = reporting_data_manager.data.copy()
            data_with_preds["preds"] = preds

            with open(report_path, "w") as report_file:
                for row in data_with_preds.itertuples():
                    home_abbrev = team_service.abbrev_from_id(row.homeTeamID)
                    away_abbrev = team_service.abbrev_from_id(row.awayTeamID)
                    pred = row.preds
                    confidence = pred if pred > 0.5 else 1 - pred
                    if row.preds > 0.5:
                        pred_winner = home_abbrev
                    else:
                        pred_winner = away_abbrev
                    report_file.write(f"Game: {home_abbrev} vs {away_abbrev}\n")
                    report_file.write(f"Predicted winner: {pred_winner}\n")
                    report_file.write(
                        f"Predicted confidence: {confidence * 100:.0f}%\n"
                    )
                    report_file.write("---\n")
