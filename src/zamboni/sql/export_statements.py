export_statements = {
    "games": """
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
        IFNULL(gpso.prevOutcome, 0) AS prevMatchupOutcome,
        IFNULL(gpso.prevInOT, 0) AS prevMatchupInOT,
        CASE WHEN gpso.prevOutcome IS NULL THEN 0 ELSE 1 END AS hasPreviousMatchup,
        games.outcome,
        games.inOT,
        games.datePlayed
    FROM games
    LEFT OUTER JOIN games_history hgh
        ON games.id=hgh.gameID AND games.homeTeamID=hgh.teamID
    LEFT OUTER JOIN games_history agh
        ON games.id=agh.gameID AND games.awayTeamID=agh.teamID
    LEFT OUTER JOIN games_prev_same_opp gpso
        ON games.id=gpso.gameID
    """,
    "games_init": """
    SELECT homeTeamID,
           awayTeamID,
           dayOfYrPlayed,
           yrPlayed,
           outcome
       FROM games
    """,
    "games_last_export": """
    SELECT lastExportDate
    FROM gamesLastExport
    LIMIT 1
    """,
    "games_with_predictions": """
    SELECT games.id,
        games.homeTeamID,
        home.nameAbbrev AS homeAbbrev,
        games.awayTeamID,
        away.nameAbbrev AS awayAbbrev,
        games.datePlayed,
        games.homeTeamGoals,
        games.awayTeamGoals,
        games.outcome,
        games.inOT,
        gp.prediction,
        p.predicterName
    FROM games
    INNER JOIN gamePredictions gp ON games.id = gp.gameID
    INNER JOIN predicterRegister p ON gp.predicterID = p.id
    INNER JOIN teams home ON games.homeTeamID = home.id
    INNER JOIN teams away ON games.awayTeamID = away.id
    WHERE p.active = 1
    AND games.datePlayed >= "{start_date}"
    AND games.datePlayed <= "{end_date}"
    """,
}
