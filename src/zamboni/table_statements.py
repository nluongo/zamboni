create_statements = {
    'players' :
    """
    CREATE TABLE players (
        id INTEGER PRIMARY KEY,
        name TEXT
        )
    """,
    'teams' :
    """
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY,
        name TEXT
        )
    """,
    'games' :
    """
    CREATE TABLE games (
        id INTEGER PRIMARY KEY,
        homeTeamID INTEGER,
        awayTeamID INTEGER,
        locationID INTEGER,
        datePlayed INTEGER,
        timePlayed INTEGER,
        seasonID INTEGER
        )
    """
    }
