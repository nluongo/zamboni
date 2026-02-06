"""
Tests for SQLAlchemy conversion in sql_handler and sql_helpers.
Tests cover upsert, parameterized queries, Core/ORM expressions, and allow-list validation.
"""

import pytest
import os
from datetime import date, timedelta
from sqlalchemy import select, text, insert

from zamboni import DBConnector, SQLHandler, TableCreator
from zamboni.sql.tables import Teams, PredicterRegister, GamePredictions, LastTraining
from zamboni.sql.sql_helpers import upsert


TEST_DB_PATH = "data/test_sqlalchemy.db"


@pytest.fixture
def test_db():
    """Create and teardown a test database."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    db_connector = DBConnector(TEST_DB_PATH)
    db_con = db_connector.connect_db()

    # Create required tables
    table_creator = TableCreator(db_con)
    table_creator.create_table("teams")
    table_creator.create_table("games")
    table_creator.create_table("players")
    table_creator.create_table("rosterEntries")
    table_creator.create_table("predicterRegister")
    table_creator.create_table("gamePredictions")
    table_creator.create_table("lastTraining")
    table_creator.create_table("gamesLastExport")

    yield db_con

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def sql_handler(test_db):
    """Create a SQLHandler instance with test database."""
    return SQLHandler(db_con=test_db)


class TestUpsertHelper:
    """Tests for the upsert() helper in sql_helpers."""

    def test_upsert_insert_new_record(self, sql_handler):
        """Test inserting a new record via upsert."""
        values = {
            "id": 1,
            "predicterName": "test_predicter",
            "predicterType": "TestType",
            "predicterPath": "/path/to/test",
            "trainable": True,
            "active": True,
        }
        upsert(
            sql_handler.db_con, PredicterRegister.__table__, values, ["predicterName"]
        )

        # Verify the record was inserted
        stmt = select(PredicterRegister).where(
            PredicterRegister.predicterName == "test_predicter"
        )
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()

        assert result is not None
        assert result.predicterName == "test_predicter"
        assert result.predicterType == "TestType"

    def test_upsert_update_existing_record(self, sql_handler):
        """Test updating an existing record via upsert (on conflict)."""
        # First insert
        values1 = {
            "predicterName": "update_test",
            "predicterType": "OriginalType",
            "predicterPath": "/original",
            "trainable": False,
            "active": True,
        }
        upsert(
            sql_handler.db_con, PredicterRegister.__table__, values1, ["predicterName"]
        )

        # Update via upsert (same predicterName key)
        values2 = {
            "predicterName": "update_test",
            "predicterType": "UpdatedType",
            "predicterPath": "/updated",
            "trainable": True,
            "active": False,
        }
        upsert(
            sql_handler.db_con, PredicterRegister.__table__, values2, ["predicterName"]
        )

        # Verify the record was updated (not duplicated)
        stmt = select(PredicterRegister).where(
            PredicterRegister.predicterName == "update_test"
        )
        with sql_handler.db_con.connect() as conn:
            results = conn.execute(stmt).fetchall()

        assert len(results) == 1
        result = results[0]
        assert result.predicterType == "UpdatedType"
        assert result.predicterPath == "/updated"
        assert result.trainable is True
        assert result.active is False

    def test_upsert_composite_key(self, sql_handler):
        """Test upsert with composite primary key (GamePredictions)."""
        # Insert initial prediction
        values1 = {
            "gameID": 100,
            "predicterID": 1,
            "prediction": 0.75,
            "predictionBinary": 1,
            "predictionDate": date.today(),
        }
        upsert(
            sql_handler.db_con,
            GamePredictions.__table__,
            values1,
            ["gameID", "predicterID"],
        )

        # Update the same prediction
        values2 = {
            "gameID": 100,
            "predicterID": 1,
            "prediction": 0.85,
            "predictionBinary": 1,
            "predictionDate": date.today(),
        }
        upsert(
            sql_handler.db_con,
            GamePredictions.__table__,
            values2,
            ["gameID", "predicterID"],
        )

        # Verify single record with updated value
        stmt = select(GamePredictions).where(
            (GamePredictions.gameID == 100) & (GamePredictions.predicterID == 1)
        )
        with sql_handler.db_con.connect() as conn:
            results = conn.execute(stmt).fetchall()

        assert len(results) == 1
        assert results[0].prediction == 0.85


class TestGetTeamId:
    """Tests for get_team_id method using parameterized select."""

    def test_get_team_id_existing_team(self, sql_handler):
        """Test retrieving team ID for existing team."""
        # Insert team
        stmt = insert(Teams).values(name="Detroit Red Wings", nameAbbrev="DET")
        with sql_handler.db_con.begin() as conn:
            conn.execute(stmt)

        # Get team ID
        id_dict = {}
        team_id = sql_handler.get_team_id(id_dict, "DET")

        assert team_id != -1
        assert id_dict["DET"] == team_id

    def test_get_team_id_nonexistent_team(self, sql_handler):
        """Test retrieving team ID for non-existent team."""
        id_dict = {}
        team_id = sql_handler.get_team_id(id_dict, "XYZ")

        assert team_id == -1

    def test_get_team_id_caches_result(self, sql_handler):
        """Test that get_team_id caches results in id_dict."""
        from sqlalchemy import insert

        # Insert team
        stmt = insert(Teams).values(name="Colorado Avalanche", nameAbbrev="COL")
        with sql_handler.db_con.begin() as conn:
            conn.execute(stmt)

        id_dict = {}
        team_id_1 = sql_handler.get_team_id(id_dict, "COL")
        team_id_2 = sql_handler.get_team_id(id_dict, "COL")

        assert team_id_1 == team_id_2
        assert id_dict["COL"] == team_id_1


class TestPredicterRegister:
    """Tests for predicter registration and upsert methods."""

    def test_add_predicter_to_register_new(self, sql_handler):
        """Test adding a new predicter to register."""
        sql_handler.add_predicter_to_register(
            name="test_predicter_v1",
            predicter_class_name="TestPredicter",
            path="/path/to/predicter",
            trainable=True,
            active=True,
        )

        predicter_id = sql_handler.predicter_id_from_name("test_predicter_v1")
        assert predicter_id > 0

    def test_add_predicter_to_register_update(self, sql_handler):
        """Test updating an existing predicter registration."""
        # Add initial
        sql_handler.add_predicter_to_register(
            name="update_pred",
            predicter_class_name="OriginalClass",
            path="/original",
            trainable=False,
            active=True,
        )
        id_1 = sql_handler.predicter_id_from_name("update_pred")

        # Update
        sql_handler.add_predicter_to_register(
            name="update_pred",
            predicter_class_name="UpdatedClass",
            path="/updated",
            trainable=True,
            active=False,
        )
        id_2 = sql_handler.predicter_id_from_name("update_pred")

        # IDs should be the same (same record)
        assert id_1 == id_2

        # Verify updated values
        stmt = select(PredicterRegister).where(PredicterRegister.id == id_1)
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()

        assert result.predicterType == "UpdatedClass"
        assert result.predicterPath == "/updated"
        assert result.trainable is True
        assert result.active is False

    def test_predicter_id_from_name_not_found(self, sql_handler):
        """Test predicter_id_from_name raises ValueError when not found."""
        with pytest.raises(ValueError, match="Could not retrieve new predicter ID"):
            sql_handler.predicter_id_from_name("nonexistent_predicter")


class TestLastTrainingDate:
    """Tests for last training date tracking."""

    def test_add_predicter_to_last_training(self, sql_handler):
        """Test adding predicter to last training table."""
        sql_handler.add_predicter_to_last_training(predicter_id=1)

        # Verify record exists
        stmt = select(LastTraining).where(LastTraining.predicterID == 1)
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()

        assert result is not None
        assert result.predicterID == 1
        assert result.lastTrainingDate is None

    def test_set_last_training_date_new(self, sql_handler):
        """Test setting last training date for new predicter."""
        sql_handler.set_last_training_date(predicter_id=2)

        date_result = sql_handler.get_last_training_date(predicter_id=2)
        assert date_result is not None
        assert isinstance(date_result, date)

    def test_set_last_training_date_update(self, sql_handler):
        """Test updating last training date."""
        from zamboni.utils import get_today_date

        # Initial set
        sql_handler.set_last_training_date(predicter_id=3)
        date_1 = sql_handler.get_last_training_date(predicter_id=3)

        # Update (should not create new record)
        sql_handler.set_last_training_date(predicter_id=3)
        date_2 = sql_handler.get_last_training_date(predicter_id=3)

        # Both should be today's date
        assert date_1 == date_2
        assert date_1 == get_today_date()

    def test_get_last_training_date_not_set(self, sql_handler):
        """Test getting last training date when not set."""
        result = sql_handler.get_last_training_date(predicter_id=999)
        assert result is None


class TestGamePredictions:
    """Tests for game prediction recording."""

    def test_record_game_prediction_new(self, sql_handler):
        """Test recording a new game prediction."""
        sql_handler.record_game_prediction(
            game_id=100,
            predicter_id=1,
            prediction=0.75,
        )

        # Verify record
        stmt = select(GamePredictions).where(
            (GamePredictions.gameID == 100) & (GamePredictions.predicterID == 1)
        )
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()

        assert result is not None
        assert result.prediction == 0.75
        assert result.predictionBinary == 1

    def test_record_game_prediction_binary_threshold(self, sql_handler):
        """Test prediction binary conversion (threshold 0.5)."""
        # Test < 0.5
        sql_handler.record_game_prediction(game_id=101, predicter_id=1, prediction=0.3)
        stmt = select(GamePredictions).where(GamePredictions.gameID == 101)
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()
        assert result.predictionBinary == 0

        # Test >= 0.5
        sql_handler.record_game_prediction(game_id=102, predicter_id=1, prediction=0.5)
        stmt = select(GamePredictions).where(GamePredictions.gameID == 102)
        with sql_handler.db_con.connect() as conn:
            result = conn.execute(stmt).first()
        assert result.predictionBinary == 1

    def test_record_game_prediction_update(self, sql_handler):
        """Test updating an existing prediction."""
        sql_handler.record_game_prediction(game_id=103, predicter_id=1, prediction=0.6)
        sql_handler.record_game_prediction(game_id=103, predicter_id=1, prediction=0.8)

        # Verify single record with updated value
        stmt = select(GamePredictions).where(GamePredictions.gameID == 103)
        with sql_handler.db_con.connect() as conn:
            results = conn.execute(stmt).fetchall()

        assert len(results) == 1
        assert results[0].prediction == 0.8

    def test_get_last_prediction_date(self, sql_handler):
        """Test retrieving last prediction date for predicter."""
        today = date.today()

        sql_handler.record_game_prediction(game_id=104, predicter_id=2, prediction=0.5)

        last_date = sql_handler.get_last_prediction_date(predicter_id=2)
        assert last_date == today


class TestActionDateValidation:
    """Tests for allow-list validation in set_action_date and get_action_date."""

    def test_set_action_date_valid_table(self, sql_handler):
        """Test setting action date for allowed table."""
        sql_handler.set_action_date("gamesLastExport", "lastExportDate", date.today())

        result = sql_handler.get_action_date("gamesLastExport", "lastExportDate")
        assert result is not None

    def test_set_action_date_invalid_table(self, sql_handler):
        """Test setting action date raises error for disallowed table."""
        with pytest.raises(ValueError, match="Invalid table_name"):
            sql_handler.set_action_date("forbidden_table", "some_column")

    def test_set_action_date_invalid_column(self, sql_handler):
        """Test setting action date raises error for disallowed column."""
        with pytest.raises(ValueError, match="Invalid table_name or column_name"):
            sql_handler.set_action_date("gamesLastExport", "wrongColumn")

    def test_get_action_date_invalid_table(self, sql_handler):
        """Test getting action date raises error for disallowed table."""
        with pytest.raises(ValueError, match="Invalid table_name"):
            sql_handler.get_action_date("forbidden_table", "some_column")

    def test_set_get_game_export_date(self, sql_handler):
        """Test set/get game export date convenience methods."""
        sql_handler.set_game_export_date()
        result = sql_handler.get_game_export_date()

        assert result is not None
        assert isinstance(result, date)
        assert result == date.today()

    def test_set_get_game_export_date_overwrites(self, sql_handler):
        """Test that game export date overwrites previous value."""
        old_date = date.today() - timedelta(days=5)

        with sql_handler.db_con.begin() as conn:
            try:
                conn.execute(text("DELETE FROM gamesLastExport"))
                conn.execute(
                    text(
                        f'INSERT INTO gamesLastExport(lastExportDate) VALUES ("{old_date}")'
                    )
                )
            except Exception:
                pass  # Table might be empty

        sql_handler.set_game_export_date()
        result = sql_handler.get_game_export_date()

        assert result == date.today()


class TestQueryWithParams:
    """Tests for parameterized query() method."""

    def test_query_with_sql_string(self, sql_handler):
        """Test query() accepts SQL string."""
        from sqlalchemy import insert as sa_insert

        # Insert test data
        stmt = sa_insert(Teams).values(name="Test Team", nameAbbrev="TST")
        with sql_handler.db_con.begin() as conn:
            conn.execute(stmt)

        df = sql_handler.query("SELECT * FROM teams WHERE nameAbbrev = 'TST'")

        assert not df.empty
        assert len(df) >= 1
        assert "nameAbbrev" in df.columns

    def test_query_with_text_and_params(self, sql_handler):
        """Test query() accepts text() with parameters."""
        from sqlalchemy import insert as sa_insert

        # Insert test data
        stmt = sa_insert(Teams).values(name="Param Team", nameAbbrev="PRM")
        with sql_handler.db_con.begin() as conn:
            conn.execute(stmt)

        sql = text("SELECT * FROM teams WHERE nameAbbrev = :abbrev")
        df = sql_handler.query(sql, params={"abbrev": "PRM"})

        assert not df.empty
        assert len(df) >= 1

    def test_query_returns_dataframe(self, sql_handler):
        """Test that query() always returns DataFrame."""
        from sqlalchemy import insert as sa_insert

        stmt = sa_insert(Teams).values(name="DF Team", nameAbbrev="DFT")
        with sql_handler.db_con.begin() as conn:
            conn.execute(stmt)

        result = sql_handler.query("SELECT * FROM teams WHERE nameAbbrev = 'DFT'")

        import pandas as pd

        assert isinstance(result, pd.DataFrame)
