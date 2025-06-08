drop_view_statements = "DROP VIEW IF EXISTS {view_name}"

create_view_statements = {
    "games_per_team": """ 
    CREATE VIEW IF NOT EXISTS games_per_team
    AS
    SELECT 
        id AS gameID,
        homeTeamID AS teamID,
        awayTeamID AS oppTeamID,
        CASE outcome WHEN 1 THEN 1 ELSE 0 END AS won,
        CASE WHEN lastPeriodTypeID != "REG" THEN 1 ELSE 0 END AS inOT,
        homeTeamGoals AS goals,
        awayTeamGoals AS oppGoals
    FROM games
    UNION ALL
    SELECT
        id AS gameID,
        awayTeamID AS teamID,
        homeTeamID AS oppTeamID,
        CASE outcome WHEN 0 THEN 1 ELSE 0 END AS won,
        CASE WHEN lastPeriodTypeID != "REG" THEN 1 ELSE 0 END AS inOT,
        awayTeamGoals AS goals,
        homeTeamGoals AS oppGoals
    FROM games
    """,
    # Each row is a game and previous game for the same team and season. This is intended to allow for calculation of wins/record to date in that season for a game
    "games_with_previous": """
    CREATE VIEW IF NOT EXISTS games_with_previous
    AS
    SELECT 
        games_per_team.gameID AS gameID,  
        games_per_team.won AS won,  
        games_per_team.inOT AS inOT,  
        games_per_team.teamID AS teamID,  
        games_per_team.oppTeamID AS oppTeamID,  
        games.datePlayed AS datePlayed,  
        games.seasonID AS seasonID,  
        other_games.id AS prevGameID,
        other_games.datePlayed AS prevDatePlayed,  
        other_games_per_team.oppTeamID AS prevOppTeamID, 
        other_games_per_team.won AS prevWon, 
        other_games_per_team.inOT AS prevInOT, 
        other_games_per_team.goals AS prevGoals,
        other_games_per_team.oppGoals AS prevOppGoals
    FROM games_per_team  
    INNER JOIN games 
        ON games_per_team.gameID = games.id  
    INNER JOIN teams 
        ON games_per_team.teamID = teams.id  
    LEFT OUTER JOIN games other_games 
        ON (games_per_team.teamID = other_games.homeTeamID  
        OR games_per_team.teamID = other_games.awayTeamID)  
        AND (games.datePlayed > other_games.datePlayed
        AND games.seasonID = other_games.seasonID)
    LEFT OUTER JOIN games_per_team other_games_per_team 
        ON other_games.id = other_games_per_team.gameID  
        AND games_per_team.teamID = other_games_per_team.teamID  
    """,
    # This holds the gameID and the date of the last game played between the same two teams
    "games_prev_same_opp": """
    CREATE VIEW IF NOT EXISTS games_prev_same_opp
    AS
    SELECT
        prevMatchup.gameID,
        gwp2.prevGameID,
        games.outcome AS prevOutcome,
        games.inOT AS prevInOT
    FROM ( 
    SELECT gameID AS gameID,
        MAX(teamID) AS teamID,
        MAX(prevDatePlayed) AS prevDatePlayed
    FROM games_with_previous
    WHERE oppTeamID=prevOppTeamID
    GROUP BY gameID ) prevMatchup
    INNER JOIN games_with_previous gwp2
        ON prevMatchup.gameID=gwp2.gameID
        AND prevMatchup.prevDatePlayed=gwp2.prevDatePlayed
        AND prevMatchup.teamID=gwp2.teamID
    LEFT OUTER JOIN games
        ON gwp2.prevGameID=games.id
    """,
    # This holds summarized historical information for each game and team
    "games_history": """
    CREATE VIEW IF NOT EXISTS games_history 
    AS
    SELECT 
        gameID,
        teamID,
        IFNULL(SUM(prevWon), 0) AS prevWonNum,
        COUNT(prevWon) AS prevNum,
        IFNULL(CAST(SUM(prevWon) AS REAL) / COUNT(*), 0) AS prevWonPercentage,
        IFNULL(CAST(SUM(prevGoals) AS REAL) / COUNT(*), 0) AS prevGoalsPerGame,
        IFNULL(CAST(SUM(prevOppGoals) AS REAL) / COUNT(*), 0) AS prevOppGoalsPerGame
    FROM games_with_previous
    GROUP BY gameID, teamID
    """,
}
