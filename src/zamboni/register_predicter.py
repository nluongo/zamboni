import argparse
from zamboni.sql.sql_handler import SQLHandler
import zamboni.predicter as predicter


def main():
    parser = argparse.ArgumentParser(
        description="Register a new predicter in the predicterRegister table."
    )
    parser.add_argument("--name", required=True, help="Name of the predicter")
    parser.add_argument(
        "--class",
        dest="predicter_class",
        required=True,
        help="Class name of the predicter (e.g., NNGamePredicter)",
    )
    parser.add_argument(
        "--path", default="", help="Path to model or resource (required if trainable)"
    )
    parser.add_argument(
        "--active",
        default=True,
        action="store_true",
        help="Set if the predicter should be active",
    )
    parser.add_argument(
        "--db", default="data/zamboni.db", help="Path to the SQLite database file"
    )
    args = parser.parse_args()

    # Check if the class exists in predicter.py
    if not hasattr(predicter, args.predicter_class):
        parser.error(f"Class '{args.predicter_class}' is not defined in predicter.py.")
    predicter_class = getattr(predicter, args.predicter_class)

    # Validate path if trainable
    if predicter_class.trainable and not args.path:
        parser.error("--path is required if a trainable Predicter class is chosen.")

    sql_handler = SQLHandler()
    sql_handler.register_predicter(
        args.name,
        predicter_class.__name__,
        args.path,
        predicter_class.trainable,
        int(args.active),
    )


if __name__ == "__main__":
    main()
