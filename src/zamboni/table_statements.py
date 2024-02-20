create_statements = {
    'players' :
    """
    CREATE TABLE players (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        teamID INTEGER,
        name TEXT
        )
    """,
    'teams' :
    """
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY,
        apiID iNTEGER,
        name TEXT,
        nameAbbrev TEXT,
        conferenceAbbrev TEXT,
        divisionAbbrev TEXT
        )
    """,
    'games' :
    """
    CREATE TABLE games (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        homeTeamID INTEGER,
        awayTeamID INTEGER,
        locationID INTEGER,
        datePlayed INTEGER,
        timePlayed INTEGER,
        seasonID INTEGER,
        homeTeamGoals INTEGER,
        awayTeamGoals INTEGER
        )
    """,
    'seasons' :
    """
    CREATE TABLE seasons (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        startYear INTEGER,
        endYear INTEGER
        )
    """
    }
