drop_table_statement = "DROP TABLE IF EXISTS {table_name};"

create_table_statements = {
    "players": """
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        name TEXT,
        firstName TEXT,
        lastName TEXT,
        number INT,
        position TEXT
        )
    """,
    "teams": """
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        name TEXT,
        nameAbbrev TEXT,
        conferenceAbbrev TEXT,
        divisionAbbrev TEXT
        )
    """,
    "games": """
    CREATE TABLE IF NOT EXISTS games (
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
        inOT INTEGER,
        recordCreated INTEGER
        )
    """,
    "seasons": """
    CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        startYear INTEGER,
        endYear INTEGER
        )
    """,
    "rosterEntries": """
    CREATE TABLE IF NOT EXISTS rosterEntries (
        id INTEGER PRIMARY KEY,
        apiID INTEGER,
        playerID INTEGER,
        teamID INTEGER,
        seasonID INTEGER,
        startYear INTEGER,
        endYear INTEGER
        )
    """,
    "gamesLastExport": """
    CREATE TABLE IF NOT EXISTS gamesLastExport (
        lastExportDate INTEGER
        )
    """,
    "lastTraining": """
    CREATE TABLE IF NOT EXISTS lastTraining (
        predicterID INTEGER PRIMARY KEY,
        lastTrainingDate INTEGER
        )
    """,
    "predicterRegister": """
    CREATE TABLE IF NOT EXISTS predicterRegister (
        id INTEGER PRIMARY KEY,
        predicterName TEXT,
        predicterType TEXT,
        predicterPath TEXT,
        trainable INTEGER,
        active INTEGER
        )
    """,
    "gamePredictions": """
    CREATE TABLE IF NOT EXISTS gamePredictions (
        gameID INTEGER NOT NULL,
        predicterID INTEGER NOT NULL,
        prediction REAL,
        predictionBinary INTEGER,
        predictionDate INTEGER,
        FOREIGN KEY (gameID) REFERENCES games(id),
        FOREIGN KEY (predicterID) REFERENCES predicterRegister(id),
        PRIMARY KEY (gameID, predicterID)
        )
    """,
}
