# export_statements = {
#    "games": """
#    SELECT id,
#        homeTeamID,
#        hgh.prevWonPercentage AS homePrevWonPercentage,
#        hgh.prevGoalsPerGame AS homePrevGoalsPerGame,
#        hgh.prevOppGoalsPerGame AS homePrevOppGoalsPerGame,
#        hgh.prevNum + 1 AS homeGameOfSeason,
#        awayTeamID,
#        agh.prevWonPercentage AS awayPrevWonPercentage,
#        agh.prevGoalsPerGame AS awayPrevGoalsPerGame,
#        agh.prevOppGoalsPerGame AS awayPrevOppGoalsPerGame,
#        agh.prevNum + 1 AS awayGameOfSeason,
#        IFNULL(gpso.prevOutcome, 0) AS prevMatchupOutcome,
#        IFNULL(gpso.prevInOT, 0) AS prevMatchupInOT,
#        CASE WHEN gpso.prevOutcome IS NULL THEN 0 ELSE 1 END AS hasPreviousMatchup,
#        games.outcome,
#        games.inOT,
#        games.datePlayed
#    FROM games
#    LEFT OUTER JOIN games_history hgh
#        ON games.id=hgh.gameID AND games.homeTeamID=hgh.teamID
#    LEFT OUTER JOIN games_history agh
#        ON games.id=agh.gameID AND games.awayTeamID=agh.teamID
#    LEFT OUTER JOIN games_prev_same_opp gpso
#        ON games.id=gpso.gameID
#    """,
#    "games_init": """
#    SELECT homeTeamID,
#           awayTeamID,
#           dayOfYrPlayed,
#           yrPlayed,
#           outcome
#       FROM games
#    """,
#    "games_last_export": """
#    SELECT lastExportDate
#    FROM gamesLastExport
#    LIMIT 1
#    """,
#    "games_with_predictions": None,
# }

# Provide a callable factory to construct a selectable for games with predictions
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_, func
from .tables import (
    Games,
    Teams,
    GamePredictions,
    PredicterRegister,
    GamesPrevSameOppView,
    GamesHistoryView,
)


def games_select(start_date, end_date):
    """Provide a selectable for games within date range to be used for training"""
    hgh = aliased(GamesHistoryView, name="hgh")
    agh = aliased(GamesHistoryView, name="agh")
    gpso = aliased(GamesPrevSameOppView, name="gpso")
    stmt = (
        select(
            Games.id,
            Games.homeTeamID,
            hgh.prevWonPercentage.label("homePrevWonPercentage"),
            hgh.prevGoalsPerGame.label("homePrevGoalsPerGame"),
            hgh.prevOppGoalsPerGame.label("homePrevOppGoalsPerGame"),
            (hgh.prevNum + 1).label("homeGameOfSeason"),
            Games.awayTeamID,
            agh.prevWonPercentage.label("awayPrevWonPercentage"),
            agh.prevGoalsPerGame.label("awayPrevGoalsPerGame"),
            agh.prevOppGoalsPerGame.label("awayPrevOppGoalsPerGame"),
            (agh.prevNum + 1).label("awayGameOfSeason"),
            func.coalesce(gpso.prevOutcome, 0).label("prevMatchupOutcome"),
            func.coalesce(gpso.prevInOT, 0).label("prevMatchupInOT"),
            (func.case([(gpso.prevOutcome.is_(None), 0)], else_=1)).label(
                "hasPreviousMatchup"
            ),
            Games.outcome,
            Games.inOT,
            Games.datePlayed,
        )
        .select_from(Games)
        .join(
            hgh,
            and_(Games.id == hgh.gameID, Games.homeTeamID == hgh.teamID),
            isouter=True,
        )
        .join(
            agh,
            and_(Games.id == agh.gameID, Games.awayTeamID == agh.teamID),
            isouter=True,
        )
        .join(gpso, Games.id == gpso.gameID, isouter=True)
    )
    if start_date:
        stmt = stmt.where(Games.datePlayed >= start_date).where(
            Games.datePlayed <= end_date
        )
    else:
        stmt = stmt.where(Games.datePlayed <= end_date)
    return stmt


def games_with_predictions_select(start_date, end_date):
    """Provide a selectable for games with predictions within date range"""
    home = aliased(Teams, name="home")
    away = aliased(Teams, name="away")
    stmt = (
        select(
            Games.id,
            Games.homeTeamID,
            home.name.label("homeTeam"),
            home.nameAbbrev.label("homeAbbrev"),
            Games.awayTeamID,
            away.name.label("awayTeam"),
            away.nameAbbrev.label("awayAbbrev"),
            Games.datePlayed,
            Games.homeTeamGoals,
            Games.awayTeamGoals,
            Games.outcome,
            Games.inOT,
            GamePredictions.prediction,
            PredicterRegister.predicterName,
        )
        .select_from(Games)
        .join(GamePredictions, Games.id == GamePredictions.gameID)
        .join(PredicterRegister, GamePredictions.predicterID == PredicterRegister.id)
        .join(home, Games.homeTeamID == home.id)
        .join(away, Games.awayTeamID == away.id)
        .where(PredicterRegister.active == 1)
        .where(Games.datePlayed >= start_date)
        .where(Games.datePlayed <= end_date)
    )
    return stmt


# Replace the placeholder None with the callable factory so callers can detect it
# export_statements["games_with_predictions"] = games_with_predictions_select
# export_statements["games"] = games_select
