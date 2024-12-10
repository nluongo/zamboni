games_per_team_statement = """ 
    CREATE VIEW IF NOT EXISTS games_per_team
    AS
        SELECT 
            id AS gameID,
            homeTeamID AS teamID,
            CASE outcome WHEN 1 THEN 1 ELSE 0 END AS won,
            CASE WHEN lastPeriodTypeID != "REG" THEN 1 ELSE 0 END AS inOT,
            homeTeamGoals AS goals,
            awayTeamGoals AS oppGoals
        FROM games
        UNION ALL
        SELECT
            id AS gameID,
            awayTeamID AS teamID,
            CASE outcome WHEN 0 THEN 1 ELSE 0 END AS won,
            CASE WHEN lastPeriodTypeID != "REG" THEN 1 ELSE 0 END AS inOT,
            awayTeamGoals AS goals,
            homeTeamGoals AS oppGoals
        FROM games
    """

# Each row is a game and previous game for the same team and season. This is intended to allow for calculation of wins/record to date in that season for a game
games_with_previous_statement = """
    CREATE VIEW IF NOT EXISTS games_with_previous
    AS
        SELECT 
			games_per_team.gameID as gameID,  
	        games_per_team.won as won,  
	        games_per_team.teamID as teamID,  
	        games.datePlayed as datePlayed,  
	        games.seasonID as seasonID,  
	        other_games.datePlayed as prevDatePlayed,  
	        other_games_per_team.won as prevWon, 
            other_games_per_team.goals as prevGoals,
            other_games_per_team.oppGoals as prevOppGoals
	    FROM games_per_team  
	    INNER JOIN games ON games_per_team.gameID = games.id  
	    INNER JOIN teams ON games_per_team.teamID = teams.id  
	    INNER JOIN games other_games ON games_per_team.teamID = other_games.homeTeamID  
	        OR games_per_team.teamID = other_games.awayTeamID  
	    INNER JOIN games_per_team other_games_per_team ON other_games.id = other_games_per_team.gameID  
	        AND games_per_team.teamID = other_games_per_team.teamID  
	    WHERE games.datePlayed > other_games.datePlayed  
	        AND games.seasonID = other_games.seasonID  
	"""
