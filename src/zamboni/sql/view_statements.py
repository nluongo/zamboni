drop_view_statement = "DROP VIEW IF EXISTS {view_name}"

create_stmt_suffixes = {}
# Each row is a game per team, so each game will appear twice, once for the home team and once for the away team
create_stmt_suffixes["games_per_team"] = """
    AS
    SELECT 
        id AS "gameID",
        "homeTeamID" AS "teamID",
        "awayTeamID" AS "oppTeamID",
        CASE outcome WHEN 1 THEN 1 ELSE 0 END AS won,
        CASE WHEN "lastPeriodTypeID" != 'REG' THEN 1 ELSE 0 END AS "inOT",
        "homeTeamGoals" AS goals,
        "homeTeamPointsAwarded" AS pointsAwarded,
        "awayTeamGoals" AS "oppGoals",
        "awayTeamPointsAwarded" AS "oppPointsAwarded"
    FROM games
    UNION ALL
    SELECT
        id AS "gameID",
        "awayTeamID" AS "teamID",
        "homeTeamID" AS "oppTeamID",
        CASE outcome WHEN 0 THEN 1 ELSE 0 END AS won,
        CASE WHEN "lastPeriodTypeID" != 'REG' THEN 1 ELSE 0 END AS "inOT",
        "awayTeamGoals" AS goals,
        "awayTeamPointsAwarded" AS pointsAwarded,
        "homeTeamGoals" AS "oppGoals",
        "homeTeamPointsAwarded" AS oppPointsAwarded
    FROM games
    """

# Each row is a game and previous game for the same team and season. This is intended to allow for calculation of wins/record to date in that season for a game
create_stmt_suffixes["games_with_previous"] = """
    AS
    SELECT 
        games_per_team."gameID" AS "gameID",  
        games_per_team."won" AS "won",  
        games_per_team."inOT" AS "inOT",  
        games_per_team."teamID" AS "teamID",  
        games_per_team."oppTeamID" AS "oppTeamID",  
        games."datePlayed" AS "datePlayed",  
        games."seasonID" AS "seasonID",  
        other_games."id" AS "prevGameID",
        other_games."datePlayed" AS "prevDatePlayed",  
        other_games_per_team."oppTeamID" AS "prevOppTeamID", 
        other_games_per_team."won" AS "prevWon", 
        other_games_per_team."inOT" AS "prevInOT", 
        other_games_per_team."goals" AS "prevGoals",
        other_games_per_team."oppGoals" AS "prevOppGoals",
        other_games_per_team."pointsAwarded" AS "prevPointsAwarded"
    FROM games_per_team  
    INNER JOIN games 
        ON games_per_team."gameID" = games.id  
    INNER JOIN teams 
        ON games_per_team."teamID" = teams.id  
    LEFT OUTER JOIN games AS other_games 
        ON (games_per_team."teamID" = other_games."homeTeamID"
        OR games_per_team."teamID" = other_games."awayTeamID")  
        AND (games."datePlayed" > other_games."datePlayed"
        AND games."seasonID" = other_games."seasonID")
    LEFT OUTER JOIN games_per_team other_games_per_team 
        ON other_games.id = other_games_per_team."gameID"  
        AND games_per_team."teamID" = other_games_per_team."teamID"  
    """
# This holds the gameID and the date of the last game played between the same two teams
create_stmt_suffixes["games_prev_same_opp"] = """
    AS
    SELECT
        prevMatchup."gameID",
        gwp2."prevGameID",
        games."outcome" AS prevOutcome,
        games."inOT" AS prevInOT
    FROM ( 
    SELECT "gameID" AS "gameID",
        MAX("teamID") AS "teamID",
        MAX("prevDatePlayed") AS "prevDatePlayed"
    FROM games_with_previous
    WHERE "oppTeamID" = "prevOppTeamID"
    GROUP BY "gameID" ) prevMatchup
    INNER JOIN games_with_previous gwp2
        ON prevMatchup."gameID"=gwp2."gameID"
        AND prevMatchup."prevDatePlayed"=gwp2."prevDatePlayed"
        AND prevMatchup."teamID"=gwp2."teamID"
    LEFT OUTER JOIN games
        ON gwp2."prevGameID"=games.id
    """
# This holds summarized historical information for each game and team
create_stmt_suffixes["games_history"] = """
    AS
    SELECT 
        "gameID",
        "teamID",
        MAX("datePlayed") AS "datePlayed",
        {null_func}(SUM("prevWon"), 0) AS "prevWonNum",
        COUNT("prevWon") AS "prevNum",
        {null_func}(CAST(SUM("prevWon") AS REAL) / COUNT(*), 0) AS "prevWonPercentage",
        {null_func}(CAST(SUM("prevGoals") AS REAL) / COUNT(*), 0) AS "prevGoalsPerGame",
        {null_func}(CAST(SUM("prevOppGoals") AS REAL) / COUNT(*), 0) AS "prevOppGoalsPerGame",
        {null_func}(CAST(SUM("prevPointsAwarded") AS INTEGER), 0) AS "pointsToDate"
    FROM games_with_previous
    GROUP BY "gameID", "teamID"
    """


def create_view_statement(view_name, dialect):
    if dialect == "postgresql":
        stmt = f"""
    CREATE OR REPLACE VIEW {view_name}"""
    else:
        stmt = f"""
    CREATE VIEW IF NOT EXISTS {view_name}"""
    suffix = create_stmt_suffixes.get(view_name)
    if view_name == "games_history":
        # Adjust for SQL dialect differences
        if dialect == "postgresql":
            suffix = suffix.format(null_func="COALESCE")
        else:
            suffix = suffix.format(null_func="IFNULL")
    stmt += suffix
    return stmt
