import datetime
import logging
from zamboni.api_download import main as download_main
from zamboni import SQLHandler, DBConnector, TableCreator
from zamboni.predicters.predicter import initialize_predicter
from zamboni.data_management import ZamboniData
from zamboni.sport import TeamService

loglevels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def run(
    data_config,
    predicters,
    earliest_date = datetime.date.fromisoformat("2025-09-01"),
    latest_date = datetime.date.fromisoformat("2026-09-01"),
    download=True,
    create_tables=True,
    force_recreate_tables=False,
    load_db=True,
    export=True,
    report=True,
    train=True,
    loglevel=logging.WARNING,
):
    loglevel = loglevels[loglevel]
    logging.basicConfig(level=loglevel)
    logger = logging.getLogger(__name__)

    data_dir = data_config["dir"]
    if data_config["use_s3"]:
        from zamboni.storage import S3Storage
        s3_storage = S3Storage(data_config)
        s3_storage.get_files()

    db_uri = data_config["db"]["uri"]

    logger.info(f'DB URI: {db_uri}')

    if download:
        download_main(data_config, start_date=earliest_date, end_date=latest_date)

    db_connector = DBConnector(db_uri)
    engine = db_connector.connect_db()
    sql_handler = SQLHandler(txt_dir=data_dir, engine=engine)

    if create_tables:
        table_creator = TableCreator(engine)
        table_creator.create_tables(overwrite=force_recreate_tables)

    if load_db or report:
        team_service = TeamService(engine)

    if load_db:
        sql_handler.load_seasons()
        sql_handler.load_teams()
        team_service.build_abbrev_id_dicts()
        sql_handler.load_games_to_db()
        sql_handler.load_predicters(predicters)
        # sql_handler.load_players()
        # sql_handler.load_roster_entries()

    if report or train:
        # predicters_service = PredicterService(sql_handler=sql_handler)
        predicters_from_db = sql_handler.get_predicters()

    if train:
        for predicter_from_db in predicters_from_db:
            if not predicter_from_db.active:
                continue
            logger.info(f"Initializing predicter: {predicter_from_db.predicterName}")
            predicter = initialize_predicter(
                id=predicter_from_db.id,
                name=predicter_from_db.predicterName,
                class_name=predicter_from_db.predicterClass,
                model_path=predicter_from_db.predicterPath,
                active=predicter_from_db.active,
                sql_handler=sql_handler
            )
            if predicter.trainable:
                last_training_date = sql_handler.get_last_training_date(predicter.id)
                logger.info(
                    f"Last training date for {predicter.name}: {last_training_date}"
                )
                new_games = sql_handler.query_games(start_date=last_training_date)
            else:
                last_prediction_date = sql_handler.get_last_prediction_date(
                    predicter.id
                )
                new_games = sql_handler.query_games(start_date=last_prediction_date)
            if len(new_games) == 0:
                continue
            games_data = ZamboniData(new_games)
            # Add preds column with predictions
            predicter.update(games_data.data)
            sql_handler.record_game_predictions(predicter.id, games_data.data)

        
    if data_config["use_s3"]:
        s3_storage.upload_files()


        # if report:
        #    todays_games = sql_handler.query_games(start_date=today_date_str())
        #    if len(todays_games) > 0:
        #        for predicter in predicters:
        #            if not predicter.active:
        #                continue
        #            logger.info(f"Running predicter: {predicter.name}")
        #            for game in todays_games.itertuples():
        #                game_id = game.id
        #                prediction = predicter.predict(game)
        #                logger.info(
        #                    f"Predicted outcome for game {game_id}: {prediction}"
        #                )
