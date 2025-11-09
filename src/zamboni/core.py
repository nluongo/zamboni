import logging
from zamboni.api_download import main as download_main
from zamboni import SQLHandler, DBConnector, TableCreator
from zamboni.predicter_service import PredicterService
from zamboni.data_management import ZamboniData
from zamboni.sport import TeamService
from zamboni.utils import today_date_str

loglevels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def run(
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

    if download:
        download_main()

    db_connector = DBConnector()
    db_con = db_connector.connect_db()
    sql_handler = SQLHandler(db_con=db_con)

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
        sql_handler.load_games_to_db()
        # sql_handler.load_players()
        # sql_handler.load_roster_entries()

    if report or train:
        predicters_service = PredicterService()
        predicters = predicters_service.get_predicters()

    if train:
        for predicter in predicters:
            if not predicter.active:
                continue
            logger.info(f"Initializing predicter: {predicter.name}")
            if predicter.trainable:
                last_training_date = sql_handler.get_last_training_date(predicter.id)
                logger.info(
                    f"Last training date for {predicter.name}: {last_training_date}"
                )
                new_games = sql_handler.query_games(after_date=last_training_date)
            else:
                last_prediction_date = sql_handler.get_last_prediction_date(
                    predicter.id
                )
                new_games = sql_handler.query_games(after_date=last_prediction_date)
            if new_games is None or len(new_games) == 0:
                continue
            games_data = ZamboniData(new_games)
            predicter.update(games_data)

        if report:
            todays_games = sql_handler.query_games(after_date=today_date_str())
            if todays_games:
                for predicter in predicters:
                    if not predicter.active:
                        continue
                    logger.info(f"Running predicter: {predicter.name}")
                    for game in todays_games.itertuples():
                        game_id = game.id
                        prediction = predicter.predict(game)
                        logger.info(
                            f"Predicted outcome for game {game_id}: {prediction}"
                        )
