create_statements = {
    'players' :
    """
    CREATE TABLE players (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        name TEXT,
        firstName TEXT,
        lastName TEXT,
        number INT,
        position TEXT
        )
    """,
    'teams' :
    """
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
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
        seasonID INTEGER,
        homeTeamID INTEGER,
        awayTeamID INTEGER,
        datePlayed INTEGER,
        dayOfYrPlayed INTEGER,
        yrPlayed INTEGER,
        timePlayed INTEGER,
        homeTeamGoals INTEGER,
        awayTeamGoals INTEGER,
        gameTypeID INTEGER,
        lastPeriodTypeID INTEGER,
        outcome INTEGER,
        inOT INTEGER
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
    """,
    'rosterEntries' :
    """
    CREATE TABLE rosterEntries (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        playerID INTEGER,
        teamID INTEGER,
        seasonID INTEGER,
        startYear INTEGER,
        endYear INTEGER
        )
    """
    }
