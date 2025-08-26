from zamboni import DBConnector, SQLHandler, TableCreator
from zamboni.sport import Game
import os

test_path = "data/test.db"


def create_db(path=test_path):
    db_connector = DBConnector(test_path)
    db_con = db_connector.connect_db()
    return db_con


def test_db_creation():
    _ = create_db()
    file_exists = os.path.exists(test_path)
    os.remove(test_path)
    assert file_exists


def test_table_creation():
    db_con = create_db()
    sql_handler = SQLHandler(db_con=db_con)
    table_creator = TableCreator(db_con)

    table_creator.create_table("teams")
    table_creator.create_table("games")

    teams_sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name='teams'"
    games_sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name='games'"
    teams_out = sql_handler.execute(teams_sql).fetchone()[0]
    games_out = sql_handler.execute(games_sql).fetchone()[0]
    os.remove(test_path)
    assert teams_out and games_out


def test_team_creation():
    db_con = create_db()
    sql_handler = SQLHandler(db_con=db_con)
    table_creator = TableCreator(db_con)

    table_creator.create_table("teams")
    table_creator.create_table("games")

    sql_handler.execute(
        "INSERT INTO teams(name, nameAbbrev) VALUES ('Detroit Red Wings', 'DET')"
    )
    sql_handler.execute(
        "INSERT INTO teams(name, nameAbbrev) VALUES ('Colorado Avalanche', 'COL')"
    )

    out = sql_handler.execute("SELECT COUNT(name) FROM teams")
    out = out.fetchone()[0]
    os.remove(test_path)
    assert out == 2


def test_game_creation():
    db_con = create_db()
    sql_handler = SQLHandler(db_con=db_con)
    table_creator = TableCreator(db_con)

    table_creator.create_table("teams")
    table_creator.create_table("games")

    sql_handler.execute(
        "INSERT INTO teams(name, nameAbbrev) VALUES ('Detroit Red Wings', 'DET')"
    )
    sql_handler.execute(
        "INSERT INTO teams(name, nameAbbrev) VALUES ('Colorado Avalanche', 'COL')"
    )

    game = Game("DET", "COL", "26-03-1997")
    game.api_id = 0
    sql_handler.insert_game(game)

    out = sql_handler.execute("SELECT COUNT(id) FROM games")
    out = out.fetchone()[0]
    os.remove(test_path)
    assert out == 1
