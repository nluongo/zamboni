game_per_team_statement = """ 
    CREATE VIEW IF NOT EXISTS games_per_team
    AS
        SELECT 
            gameID,
            homeTeamID AS teamID
            CASE outcome WHEN 1 THEN 1 ELSE 0 AS won
            CASE outcome WHEN 0 THEN 1 ELSE 0 AS tied
        UNION ALL
        SELECT
            gameID,
            awayTeamID AS teamID
            CASE outcome WHEN 0 THEN 1 ELSE 0 AS won
            CASE outcome WHEN 0 THEN 1 ELSE 0 AS tied
    """
