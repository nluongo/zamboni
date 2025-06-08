import argparse
import sys
from datetime import datetime
from zamboni import SQLHandler, PredicterService


def main():
    parser = argparse.ArgumentParser(
        description="Backtest a Predicter class over historical games."
    )
    parser.add_argument(
        "--predicter-name",
        type=str,
        required=True,
        help="Import path to Predicter class (e.g., mymodule.NNGamePredicter)",
    )
    parser.add_argument(
        "--games",
        type=str,
        default="data/games.txt",
        help="Path to historical games file",
    )
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
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
        print(f"Predicter '{predicter_name}' not found in database.")
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

    # Evaluate predicter
    correct = 0
    total = 0
    for index, game in games_df.iterrows():
        game = game.to_dict()
        prediction = predicter.predict(game)
        try:
            # Assuming 'outcome' is a column with 1 for home win, 0 for away win
            actual = game["outcome"]
        except Exception:
            continue
        if prediction == actual:
            correct += 1
        total += 1
        if args.record:
            # Record the prediction and actual outcome
            sql_handler.record_game_prediction(game["id"], predicter.id, prediction)

    accuracy = correct / total if total else 0
    print(f"Backtest completed: {correct}/{total} correct ({accuracy:.2%} accuracy)")


if __name__ == "__main__":
    main()
