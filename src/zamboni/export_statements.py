export_statements = {
    'games' :
    """
    SELECT id,
        homeTeamID,
        hgh.prevWonPercentage AS homePrevWonPercentage,
        hgh.prevGoalsPerGame AS homePrevGoalsPerGame,
        hgh.prevOppGoalsPerGame AS homePrevOppGoalsPerGame,
        hgh.prevNum + 1 AS homeGameOfSeason,
        awayTeamID,
        agh.prevWonPercentage AS awayPrevWonPercentage,
        agh.prevGoalsPerGame AS awayPrevGoalsPerGame,
        agh.prevOppGoalsPerGame AS awayPrevOppGoalsPerGame,
        agh.prevNum + 1 AS awayGameOfSeason,
        games.outcome
    FROM games
    LEFT OUTER JOIN games_history hgh
        ON games.id=hgh.gameID AND games.homeTeamID=hgh.teamID
    LEFT OUTER JOIN games_history agh
        ON games.id=agh.gameID AND games.awayTeamID=agh.teamID
    """,
    'games_init' :
    """
    SELECT homeTeamID,
           awayTeamID,
           dayOfYrPlayed,
           yrPlayed,
           outcome
       FROM games
    """,
    }
