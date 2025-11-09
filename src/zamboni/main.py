import argparse

from zamboni.core import run


def cli():
    parser = argparse.ArgumentParser(description="Process NHL data pipeline.")

    # Flag to control downloading NHL data.
    parser.add_argument("--download", action="store_true", help="Download NHL data")
    parser.add_argument(
        "--no-download",
        dest="download",
        action="store_false",
        help="Skip downloading NHL data",
    )
    parser.set_defaults(download=True)

    # Flag to control creating tables in the database.
    parser.add_argument(
        "--create-tables", action="store_true", help="Create database tables"
    )
    parser.add_argument(
        "--no-create-tables",
        dest="create_tables",
        action="store_false",
        help="Skip creating tables",
    )
    parser.set_defaults(create_tables=True)

    # Flag to delete and recreate all tables and views
    parser.add_argument(
        "--force-recreate-tables",
        dest="force_recreate_tables",
        action="store_true",
        help="Force deletion and re-creation of all tables and views",
    )
    parser.set_defaults(force_recreate_tables=False)

    # Flag to control loading data into the database.
    parser.add_argument(
        "--load-db", action="store_true", help="Load data into the database"
    )
    parser.add_argument(
        "--no-load-db",
        dest="load_db",
        action="store_false",
        help="Skip loading data into the database",
    )
    parser.set_defaults(load_db=True)

    # Flag to control exporting the data.
    parser.add_argument("--export", action="store_true", help="Export data")
    parser.add_argument(
        "--no-export", dest="export", action="store_false", help="Skip data export"
    )
    parser.set_defaults(export=True)

    # Flag to control reporting predictions for today's games.
    parser.add_argument(
        "--report", action="store_true", help="Report predictions for today's games"
    )
    parser.add_argument(
        "--no-report", dest="report", action="store_false", help="Skip data report"
    )
    parser.set_defaults(report=True)

    # Flag to control training the model.
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument(
        "--no-train", dest="train", action="store_false", help="Skip training the model"
    )
    parser.set_defaults(train=True)

    # Set log level
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="loglevel",
        help="Logging level",
    )
    parser.set_defaults(loglevel="WARNING")

    args = parser.parse_args()
    download = args.download
    create_tables = args.create_tables
    load_db = args.load_db
    export = args.export
    report = args.report
    train = args.train
    force_recreate_tables = args.force_recreate_tables
    loglevel = args.loglevel

    run(
        download=download,
        create_tables=create_tables,
        force_recreate_tables=force_recreate_tables,
        load_db=load_db,
        export=export,
        report=report,
        train=train,
        loglevel=loglevel,
    )


if __name__ == "__main__":
    cli()
