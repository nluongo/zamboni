from sqlalchemy import Integer, Text, Date, Time, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Players(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apiID: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    firstName: Mapped[str] = mapped_column(Text)
    lastName: Mapped[str] = mapped_column(Text)
    number: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(Text)


class Teams(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apiID: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    nameAbbrev: Mapped[str] = mapped_column(Text, unique=True)
    conferenceAbbrev: Mapped[str] = mapped_column(Text)
    divisionAbbrev: Mapped[str] = mapped_column(Text)


class Games(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apiID: Mapped[int] = mapped_column(Integer)
    seasonID: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    homeTeamID: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    awayTeamID: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    datePlayed: Mapped[Date] = mapped_column(Date)
    dayOfYrPlayed: Mapped[int] = mapped_column(Integer)
    yrPlayed: Mapped[int] = mapped_column(Integer)
    timePlayed: Mapped[Time] = mapped_column(Time)
    homeTeamGoals: Mapped[int | None] = mapped_column(Integer)
    awayTeamGoals: Mapped[int | None] = mapped_column(Integer)
    gameTypeID: Mapped[int] = mapped_column(Integer)
    lastPeriodTypeID: Mapped[str] = mapped_column(Text)
    outcome: Mapped[int] = mapped_column(Integer)
    inOT: Mapped[bool | None] = mapped_column(Boolean)
    recordCreated: Mapped[Date] = mapped_column(Date)


class Seasons(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apiID: Mapped[int] = mapped_column(Integer, unique=True)
    startYear: Mapped[int] = mapped_column(Integer)
    endYear: Mapped[int] = mapped_column(Integer)


class RosterEntries(Base):
    __tablename__ = "rosterEntries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apiID: Mapped[int] = mapped_column(Integer)
    playerID: Mapped[int] = mapped_column(ForeignKey("players.id"))
    teamID: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    seasonID: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    startYear: Mapped[int] = mapped_column(Integer)
    endYear: Mapped[int] = mapped_column(Integer)


# class GamesLastExport(Base):
#    __tablename__ = "gamesLastExport"
#
#    lastExportDate: Mapped[int] = mapped_column(Integer)


class LastTraining(Base):
    __tablename__ = "lastTraining"

    predicterID: Mapped[int] = mapped_column(Integer, primary_key=True)
    lastTrainingDate: Mapped[Date] = mapped_column(Date)


class PredicterRegister(Base):
    __tablename__ = "predicterRegister"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    predicterName: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    predicterType: Mapped[str] = mapped_column(Text)
    predicterPath: Mapped[str] = mapped_column(Text)
    trainable: Mapped[bool] = mapped_column(Boolean)
    active: Mapped[bool] = mapped_column(Boolean)


class GamePredictions(Base):
    __tablename__ = "gamePredictions"

    gameID: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    predicterID: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    prediction: Mapped[float] = mapped_column(Float)
    predictionBinary: Mapped[bool] = mapped_column(Boolean)
    predictionDate: Mapped[Date] = mapped_column(Date)


class GamesPerTeamView(Base):
    __tablename__ = "games_per_team"

    gameID: Mapped[int] = mapped_column(Integer, primary_key=True)
    teamID: Mapped[int] = mapped_column(Integer)
    oppTeamID: Mapped[int] = mapped_column(Integer)
    won: Mapped[bool] = mapped_column(Boolean)
    inOT: Mapped[bool] = mapped_column(Boolean)
    goals: Mapped[int] = mapped_column(Integer)
    oppGoals: Mapped[int] = mapped_column(Integer)


class GamesWithPreviousView(Base):
    __tablename__ = "games_with_previous"

    gameID: Mapped[int] = mapped_column(Integer, primary_key=True)
    won: Mapped[bool] = mapped_column(Boolean)
    inOT: Mapped[bool] = mapped_column(Boolean)
    teamID: Mapped[int] = mapped_column(Integer)
    oppTeamID: Mapped[int] = mapped_column(Integer)
    datePlayed: Mapped[Date] = mapped_column(Date)
    seasonID: Mapped[int] = mapped_column(Integer)
    prevGameID: Mapped[int] = mapped_column(Integer)
    prevDatePlayed: Mapped[Date] = mapped_column(Date)
    prevOppTeamID: Mapped[int] = mapped_column(Integer)
    prevWon: Mapped[bool] = mapped_column(Boolean)
    prevInOT: Mapped[bool] = mapped_column(Boolean)
    prevGoals: Mapped[int] = mapped_column(Integer)
    prevOppGoals: Mapped[int] = mapped_column(Integer)


class GamesPrevSameOppView(Base):
    __tablename__ = "games_prev_same_opp"

    gameID: Mapped[int] = mapped_column(Integer, primary_key=True)
    prevGameID: Mapped[int] = mapped_column(Integer)
    prevOutcome: Mapped[int] = mapped_column(Integer)
    prevInOT: Mapped[bool] = mapped_column(Boolean)


class GamesHistoryView(Base):
    __tablename__ = "games_history"

    gameID: Mapped[int] = mapped_column(Integer, primary_key=True)
    teamID: Mapped[int] = mapped_column(Integer)
    oppTeamID: Mapped[int] = mapped_column(Integer)
    gamesPlayed: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    otLosses: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)
    goalsFor: Mapped[int] = mapped_column(Integer)
    goalsAgainst: Mapped[int] = mapped_column(Integer)
    avgGoalsFor: Mapped[float] = mapped_column(Float)
    avgGoalsAgainst: Mapped[float] = mapped_column(Float)
    winPct: Mapped[float] = mapped_column(Float)
    pointsPct: Mapped[float] = mapped_column(Float)


table_class_names = [
    Players,
    Games,
    Teams,
    Seasons,
    RosterEntries,
    LastTraining,
    PredicterRegister,
    GamePredictions,
]
table_classes = {cls.__tablename__: cls for cls in table_class_names}
view_class_names = [
    GamesPerTeamView,
    GamesWithPreviousView,
    GamesPrevSameOppView,
    GamesHistoryView,
]
view_classes = {cls.__tablename__: cls for cls in view_class_names}

# drop_table_statement = "DROP TABLE IF EXISTS {table_name};"
#
# create_table_statements = {
#    "players": """
#    CREATE TABLE IF NOT EXISTS players (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#
# drop_table_statement = "DROP TABLE IF EXISTS {table_name};"
#
# create_table_statements = {
#    "players": """
#    CREATE TABLE IF NOT EXISTS players (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#        name TEXT,
#        firstName TEXT,
#        lastName TEXT,
#        number INT,
#        position TEXT
#        )
#    """,
#    "teams": """
#    CREATE TABLE IF NOT EXISTS teams (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#        name TEXT,
#        nameAbbrev TEXT,
#        conferenceAbbrev TEXT,
#        divisionAbbrev TEXT
#        )
#    """,
#    "games": """
#    CREATE TABLE IF NOT EXISTS games (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#        seasonID INTEGER,
#        homeTeamID INTEGER,
#        awayTeamID INTEGER,
#        datePlayed INTEGER,
#        dayOfYrPlayed INTEGER,
#        yrPlayed INTEGER,
#        timePlayed INTEGER,
#        homeTeamGoals INTEGER,
#        awayTeamGoals INTEGER,
#        gameTypeID INTEGER,
#        lastPeriodTypeID INTEGER,
#        outcome INTEGER,
#        inOT INTEGER,
#        recordCreated INTEGER
#        )
#    """,
#    "seasons": """
#    CREATE TABLE IF NOT EXISTS seasons (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#        startYear INTEGER,
#        endYear INTEGER
#        )
#    """,
#    "rosterEntries": """
#    CREATE TABLE IF NOT EXISTS rosterEntries (
#        id INTEGER PRIMARY KEY,
#        apiID INTEGER,
#        playerID INTEGER,
#        teamID INTEGER,
#        seasonID INTEGER,
#        startYear INTEGER,
#        endYear INTEGER
#        )
#    """,
#    "gamesLastExport": """
#    CREATE TABLE IF NOT EXISTS gamesLastExport (
#        lastExportDate INTEGER
#        )
#    """,
#    "lastTraining": """
#    CREATE TABLE IF NOT EXISTS lastTraining (
#        predicterID INTEGER PRIMARY KEY,
#        lastTrainingDate INTEGER
#        )
#    """,
#    "predicterRegister": """
#    CREATE TABLE IF NOT EXISTS predicterRegister (
#        id INTEGER PRIMARY KEY,
#        predicterName TEXT UNIQUE NOT NULL,
#        predicterType TEXT,
#        predicterPath TEXT,
#        trainable INTEGER,
#        active INTEGER
#        )
#    """,
#    "gamePredictions": """
#    CREATE TABLE IF NOT EXISTS gamePredictions (
#        gameID INTEGER NOT NULL,
#        predicterID INTEGER NOT NULL,
#        prediction REAL,
#        predictionBinary INTEGER,
#        predictionDate INTEGER,
#        FOREIGN KEY (gameID) REFERENCES games(id),
#        FOREIGN KEY (predicterID) REFERENCES predicterRegister(id),
#        PRIMARY KEY (gameID, predicterID)
#        )
#    """,
# }
