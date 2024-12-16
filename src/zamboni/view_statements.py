view_statements = {
    'games_per_team' :
    """ 
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
    'games_with_previous' :
    """
    CREATE VIEW IF NOT EXISTS games_with_previous
    AS
        SELECT 
			games_per_team.gameID AS gameID,  
	        games_per_team.won AS won,  
	        games_per_team.teamID AS teamID,  
	        games_per_team.oppTeamID AS oppTeamID,  
	        games.datePlayed AS datePlayed,  
	        games.seasonID AS seasonID,  
            other_games.id AS prevGameID,
	        other_games.datePlayed AS prevDatePlayed,  
	        other_games_per_team.oppTeamID AS prevOppTeamID, 
	        other_games_per_team.won AS prevWon, 
            other_games_per_team.goals AS prevGoals,
            other_games_per_team.oppGoals AS prevOppGoals
	    FROM games_per_team  
	    INNER JOIN games ON games_per_team.gameID = games.id  
	    INNER JOIN teams ON games_per_team.teamID = teams.id  
	    INNER JOIN games other_games ON games_per_team.teamID = other_games.homeTeamID  
	        OR games_per_team.teamID = other_games.awayTeamID  
	    INNER JOIN games_per_team other_games_per_team ON other_games.id = other_games_per_team.gameID  
	        AND games_per_team.teamID = other_games_per_team.teamID  
	    WHERE games.datePlayed > other_games.datePlayed  
	        AND games.seasonID = other_games.seasonID  
	""",
# This holds the gameID and the date of the last game played between the same two teams
    'games_prev_same_opp':
	"""
    CREATE VIEW IF NOT EXISTS games_prev_same_opp
    AS
        SELECT gameID AS gameID,
	    	MAX(prevDatePlayed) AS prevSameOppDatePlayed
	    FROM games_with_previous
	    WHERE oppTeamID=prevOppTeamID
	    GROUP BY gameID
    """
    }
