from datetime import date
from sqlalchemy import insert, update, and_, text
from sqlalchemy.exc import IntegrityError
from zamboni.db_con import DBConnector


def upsert(engine, table, values, primary_key_columns):
    """
    Perform an upsert (insert or update) for the given table using a dialect-aware
    strategy.

    - For PostgreSQL and SQLite (modern SQLAlchemy support), use
      insert(...).on_conflict_do_update(...).
    - For other backends, try an INSERT and fall back to UPDATE on
      IntegrityError raised for unique constraint violations.

    Parameters
    - engine: SQLAlchemy Engine
    - table: SQLAlchemy Table or declarative-mapped table
    - values: dict of column -> value
    - primary_key_columns: list of column names (strings) or Column objects

    Returns the executed ResultProxy-like object.
    """
    dialect = engine.dialect.name

    # Normalize primary_key_columns to column names if Column objects were passed
    pk_names = [getattr(col, "name", col) for col in primary_key_columns]

    if dialect in ("postgresql", "sqlite"):
        stmt = (
            insert(table)
            .values(**values)
            .on_conflict_do_update(
                index_elements=pk_names,
                set_=values,
            )
        )
        with engine.begin() as connection:
            return connection.execute(stmt)

    # Fallback for other dialects: try insert, on unique constraint conflict do update
    with engine.begin() as connection:
        try:
            return connection.execute(insert(table).values(**values))
        except IntegrityError:
            # Build WHERE clause matching primary key columns from provided values
            conditions = []
            for pk in pk_names:
                if pk not in values:
                    raise ValueError(f"Primary key column '{pk}' missing from values")
                conditions.append(getattr(table.c, pk) == values[pk])
            where_clause = and_(*conditions)

            update_values = {k: v for k, v in values.items() if k not in pk_names}
            if not update_values:
                # Nothing to update; return a fake empty result
                return connection.execute(text("SELECT 1"))

            stmt = update(table).where(where_clause).values(**update_values)
            return connection.execute(stmt)


def days_games(days_date=date.today()):
    db_connector = DBConnector()
    db_con = db_connector.connect_db()

    year, month, day = days_date.split("-")
    query_sql = f'''SELECT home_teams.nameAbbrev,
                            games.homeTeamGoals,
                            away_teams.nameAbbrev,
                            games.awayTeamGoals
                    FROM games 
                    LEFT OUTER JOIN teams home_teams ON games.homeTeamID = home_teams.id
                    LEFT OUTER JOIN teams away_teams ON games.awayTeamID = away_teams.id
                    WHERE datePlayed="{days_date}"'''
    with db_con as cursor:
        query_res = cursor.execute(query_sql)
        games = query_res.fetchall()

    return games


if __name__ == "__main__":
    days_games("2025-02-09")
