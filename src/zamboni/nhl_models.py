"""
Pydantic models for NHL API responses.

These models validate the structure and content of responses from the NHL API
before they are processed by the application.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, field_validator, model_validator


# ============================================================================
# Team Models
# ============================================================================


class TeamDetails(BaseModel):
    """Team information embedded in a game response."""

    id: int
    abbrev: str
    commonName: Dict[str, str]
    placeName: Dict[str, str]
    placeNameWithPreposition: Dict[str, str]
    score: Optional[int] = None
    logo: Optional[str] = None
    darkLogo: Optional[str] = None
    awaySplitSquad: Optional[bool] = None
    homeSplitSquad: Optional[bool] = None

    @field_validator("score")
    @classmethod
    def score_non_negative(cls, v: int) -> int:
        """Validate that scores are non-negative."""
        if v < 0:
            raise ValueError("Score cannot be negative")
        return v

    # @field_validator("id")
    # @classmethod
    # def team_id_valid(cls, v: int) -> int:
    #    """Validate that team ID is in a reasonable range."""
    #    # NHL team IDs typically range from 1 to 30+
    #    if v < 1 or v > 100:
    #        raise ValueError("Team ID out of valid range")
    #    return v


class LocalizedString(BaseModel):
    """Localized string (e.g., firstName, lastName)."""

    default: str
    fr: Optional[str] = None


# ============================================================================
# Game Models
# ============================================================================


class GameVenue(BaseModel):
    """Venue information."""

    default: str


class PeriodDescriptor(BaseModel):
    """Period information."""

    number: Optional[int] = None
    periodType: Optional[str] = None
    maxRegulationPeriods: int


class GameOutcome(BaseModel):
    """Game outcome information."""

    lastPeriodType: Optional[str] = None


class Player(BaseModel):
    """Player reference in game (scorer/goalie)."""

    playerId: int
    firstInitial: Dict[str, str]
    lastName: Dict[str, str]


class TVBroadcast(BaseModel):
    """TV broadcast information."""

    id: int
    market: str
    countryCode: str
    network: str
    sequenceNumber: int


class Game(BaseModel):
    """Complete game information from schedule endpoint."""

    id: int
    season: int
    gameType: int
    venue: GameVenue
    neutralSite: bool
    startTimeUTC: str
    easternUTCOffset: str
    venueUTCOffset: str
    venueTimezone: str
    gameState: str
    gameScheduleState: str
    tvBroadcasts: List[TVBroadcast]
    awayTeam: TeamDetails
    homeTeam: TeamDetails
    periodDescriptor: PeriodDescriptor
    gameOutcome: Optional[GameOutcome] = None
    threeMinRecap: Optional[str] = None
    threeMinRecapFr: Optional[str] = None
    condensedGame: Optional[str] = None
    condensedGameFr: Optional[str] = None
    gameCenterLink: Optional[str] = None
    winningGoalie: Optional[Player] = None
    winningGoalScorer: Optional[Player] = None

    @field_validator("startTimeUTC")
    @classmethod
    def validate_datetime(cls, v: str) -> str:
        """Validate ISO 8601 datetime format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 datetime: {v}")
        return v

    @field_validator("season")
    @classmethod
    def validate_season(cls, v: int) -> int:
        """Validate season format (e.g., 20242025)."""
        season_str = str(v)
        if len(season_str) != 8:
            raise ValueError(f"Invalid season format: {v}")
        return v

    # Not using values of gameType for now so no need to validate
    #@field_validator("gameType")
    #@classmethod
    #def validate_game_type(cls, v: int) -> int:
    #    """Validate game type (1=preseason, 2=regular, 3=playoffs, 4=all-star, 9=Olympic, 12=international(?), 19=?)."""
    #    if v not in [1, 2, 3, 4, 9, 12, 19]:
    #        raise ValueError(f"Invalid game type: {v}")
    #    return v

    @field_validator("gameState")
    @classmethod
    def validate_game_state(cls, v: str) -> str:
        """Validate game state. Don't have full list, so adding as they are encountered."""
        valid_states = {"OFF", "FINAL", "FUT", "LIVE", "CRIT", "PRE"}
        if v not in valid_states:
            raise ValueError(f"Invalid game state: {v}")
        return v

    @model_validator(mode="after")
    def validate_finished_state(self) -> "Game":
        """Validate game outcome (should only be None for games being played today)."""
        if (
            self.gameOutcome is None
            or self.awayTeam.score is None
            or self.homeTeam.score is None
        ) and self.gameState in ["FINAL", "OFF"]:
            raise ValueError(
                "Game outcome and scores must be provided for finished games."
            )
        return self


class GameDay(BaseModel):
    """Games for a single day."""

    date: str
    dayAbbrev: str
    numberOfGames: int
    games: List[Game]

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate YYYY-MM-DD date format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid date format: {v}")
        return v


class GameScheduleResponse(BaseModel):
    """Response from NHL schedule endpoint."""

    nextStartDate: Optional[str] = None
    previousStartDate: str
    gameWeek: List[GameDay]


# ============================================================================
# Player Models
# ============================================================================


class PlayerResponse(BaseModel):
    """Player information from player endpoint."""

    firstName: LocalizedString
    lastName: LocalizedString
    sweaterNumber: Optional[int] = None
    position: Optional[str] = None

    @field_validator("sweaterNumber")
    @classmethod
    def validate_sweater_number(cls, v: Optional[int]) -> Optional[int]:
        """Validate sweater number is in reasonable range."""
        if v is not None and (v < 0 or v > 99):
            raise ValueError(f"Invalid sweater number: {v}")
        return v

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: Optional[str]) -> Optional[str]:
        """Validate position is a known NHL position."""
        valid_positions = {"C", "L", "R", "D", "G", "U"}
        if v is not None and v not in valid_positions:
            raise ValueError(f"Invalid position: {v}")
        return v


# ============================================================================
# Standings Models
# ============================================================================


class StandingsEntry(BaseModel):
    """Complete standings entry for a single team."""

    # Team identification
    # teamName: Dict[str, str]
    # teamCommonName: Dict[str, str]
    # teamAbbrev: Dict[str, str]
    teamName: LocalizedString
    teamCommonName: LocalizedString
    teamAbbrev: LocalizedString
    teamLogo: Optional[str] = None
    placeName: Dict[str, str]
    seasonId: int

    # Conference and division
    conferenceAbbrev: str
    conferenceName: str
    divisionAbbrev: str
    divisionName: str

    # Sequence numbers (rankings)
    conferenceSequence: int
    conferenceHomeSequence: int
    conferenceRoadSequence: int
    conferenceL10Sequence: int
    divisionSequence: int
    divisionHomeSequence: int
    divisionRoadSequence: int
    divisionL10Sequence: int
    leagueSequence: int
    leagueHomeSequence: int
    leagueRoadSequence: int
    leagueL10Sequence: int
    waiversSequence: int
    wildcardSequence: int

    # Game metadata
    gamesPlayed: int
    gameTypeId: int
    date: str

    # Overall record
    wins: int
    losses: int
    otLosses: int
    ties: int
    points: int
    pointPctg: float
    winPctg: float

    # Regulation + OT record
    regulationWins: int
    regulationPlusOtWins: int
    regulationWinPctg: float
    regulationPlusOtWinPctg: float

    # Goals
    goalFor: int
    goalAgainst: int
    goalDifferential: int
    goalsForPctg: float
    goalDifferentialPctg: float

    # Home games
    homeGamesPlayed: int
    homeWins: int
    homeLosses: int
    homeOtLosses: int
    homeTies: int
    homePoints: int
    homeRegulationWins: int
    homeRegulationPlusOtWins: int
    homeGoalsFor: int
    homeGoalsAgainst: int
    homeGoalDifferential: int

    # Road games
    roadGamesPlayed: int
    roadWins: int
    roadLosses: int
    roadOtLosses: int
    roadTies: int
    roadPoints: int
    roadRegulationWins: int
    roadRegulationPlusOtWins: int
    roadGoalsFor: int
    roadGoalsAgainst: int
    roadGoalDifferential: int

    # Last 10 games
    l10GamesPlayed: int
    l10Wins: int
    l10Losses: int
    l10OtLosses: int
    l10Ties: int
    l10Points: int
    l10RegulationWins: int
    l10RegulationPlusOtWins: int
    l10GoalsFor: int
    l10GoalsAgainst: int
    l10GoalDifferential: int

    # Streak
    streakCode: str
    streakCount: int

    # Shootout
    shootoutWins: int
    shootoutLosses: int

    @field_validator(
        "gamesPlayed", "homeGamesPlayed", "roadGamesPlayed", "l10GamesPlayed"
    )
    @classmethod
    def non_negative_games(cls, v: int) -> int:
        """Validate games are non-negative."""
        if v < 0:
            raise ValueError("Games cannot be negative")
        return v

    @field_validator("wins", "losses", "otLosses", "ties", "points")
    @classmethod
    def non_negative_record(cls, v: int) -> int:
        """Validate record values are non-negative."""
        if v < 0:
            raise ValueError("Record value cannot be negative")
        return v

    @field_validator(
        "goalFor",
        "goalAgainst",
        "homeGoalsFor",
        "homeGoalsAgainst",
        "roadGoalsFor",
        "roadGoalsAgainst",
        "l10GoalsFor",
        "l10GoalsAgainst",
    )
    @classmethod
    def non_negative_goals(cls, v: int) -> int:
        """Validate goals are non-negative."""
        if v < 0:
            raise ValueError("Goals cannot be negative")
        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid date format: {v}")
        return v


class StandingsResponse(BaseModel):
    """Response from NHL standings endpoint."""

    wildCardIndicator: bool
    standings: List[StandingsEntry]


# ============================================================================
# Roster Models
# ============================================================================


class RosterPlayer(BaseModel):
    """Player in a roster."""

    id: int
    firstName: LocalizedString
    lastName: LocalizedString
    sweaterNumber: int
    position: str
    status: str

    @field_validator("sweaterNumber")
    @classmethod
    def validate_sweater_number(cls, v: int) -> int:
        """Validate sweater number is in reasonable range."""
        if v < 0 or v > 99:
            raise ValueError(f"Invalid sweater number: {v}")
        return v

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: str) -> str:
        """Validate position is a known NHL position."""
        valid_positions = {"C", "L", "R", "D", "G"}
        if v not in valid_positions:
            raise ValueError(f"Invalid position: {v}")
        return v


class RosterResponse(BaseModel):
    """Response from NHL roster endpoint."""

    season: int
    forwards: List[RosterPlayer]
    defensemen: List[RosterPlayer]
    goalies: List[RosterPlayer]
