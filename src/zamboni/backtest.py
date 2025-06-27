import argparse
import logging
import numpy as np
import sys
from datetime import datetime
from zamboni import SQLHandler, PredicterService
from zamboni.training import ResultsAnalyzer
from zamboni.data_management import ZamboniData, ColumnTracker
from zamboni.utils import today_date_str

logging.basicConfig(level=logging.ERROR)


def main():
    parser = argparse.ArgumentParser(
        description="Backtest a Predicter class over historical games."
    )
    parser.add_argument(
        "--predicter-name",
        type=str,
        required=True,
        help="Name of the predicter in gamePredictions.name from DB",
    )
    parser.add_argument(
        "--games",
        type=str,
        default="data/games.txt",
        help="Path to historical games file",
    )
    parser.add_argument(
        "--start-date", default="1900-01-01", type=str, help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", default=today_date_str(), type=str, help="End date (YYYY-MM-DD)"
    )
    parser.add_argument("--model-path", type=str, help="Path to model file (optional)")
    parser.add_argument(
        "--record",
        type=bool,
        help="Whether to record predictions in the database",
        default=False,
    )
    args = parser.parse_args()

    sql_handler = SQLHandler()

    predicter_name = args.predicter_name

    predicter_service = PredicterService()
    loaded_predicters = predicter_service.get_predicters()
    loaded_predicter_names = [predicter.name for predicter in loaded_predicters]
    if predicter_name not in loaded_predicter_names:
        logging.error(f"Predicter '{predicter_name}' not found in database.")
        sys.exit(1)
    for loaded_predicter in loaded_predicters:
        if loaded_predicter.name == predicter_name:
            predicter = loaded_predicter
            break

    # Parse dates
    start_date = (
        datetime.fromisoformat(args.start_date).date() if args.start_date else None
    )
    end_date = datetime.fromisoformat(args.end_date).date() if args.end_date else None

    # Load games
    games_df = sql_handler.query_games(start_date, end_date)
    column_tracker = ColumnTracker(games_df.columns.tolist())
    home_mask = games_df["homeTeamID"] > -1
    away_mask = games_df["awayTeamID"] > -1
    known_teams_mask = home_mask & away_mask
    games_df = games_df[known_teams_mask]
    zamboni_data = ZamboniData(games_df, column_tracker=column_tracker)

    if predicter.trainable:
        predicter.get_trainer(zamboni_data, overwrite=True)
        _, preds, labels = predicter.run_strategy()
        logging.debug(preds)
        logging.debug(max(preds))
    else:
        preds = np.array(
            [predicter.predict(game) for game in zamboni_data.data.itertuples()]
        )
        labels = zamboni_data.data["outcome"].values
    for i in range(len(games_df)):
        game = games_df.iloc[[i]]
        game_id = game["id"].item()
        if not predicter.trainable:
            prediction = predicter.predict(game)
        else:
            prediction = preds[i]
        sql_handler.record_game_prediction(game_id, predicter.id, prediction)

    results = ResultsAnalyzer(preds, labels)
    print(f"Accuracy at 50%: {results.get_accuracy():.2%}")
    print(f"Accuracy at 60%: {results.get_accuracy(0.6):.2%}")
    print(f"Accuracy at 70%: {results.get_accuracy(0.7):.2%}")
    print(f"Accuracy at 80%: {results.get_accuracy(0.8):.2%}")
    print(f"Accuracy at 90%: {results.get_accuracy(0.9):.2%}")

    if predicter.trainable and predicter.model_init:
        predicter.model_init.save_model(
            predicter.model_path,
            predicter.trainer.end_epoch,
            predicter.trainer.end_loss,
        )


if __name__ == "__main__":
    main()
