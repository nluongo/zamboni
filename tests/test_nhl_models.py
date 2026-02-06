"""
Unit tests for NHL API Pydantic models.

Tests validate model parsing, field constraints, and error handling
for NHL API responses.
"""

import pytest
from pydantic import ValidationError

from zamboni.nhl_models import (
    Game,
    GameDay,
    GameScheduleResponse,
    TeamDetails,
    PlayerResponse,
    StandingsEntry,
    StandingsResponse,
    RosterResponse,
)


# ============================================================================
# Team Models Tests
# ============================================================================


class TestTeamDetails:
    """Test TeamDetails model."""

    def test_valid_team(self):
        """Test parsing valid team data."""
        team_data = {
            "id": 6,
            "abbrev": "BOS",
            "commonName": {"default": "Bruins"},
            "placeName": {"default": "Boston"},
            "placeNameWithPreposition": {"default": "Boston", "fr": "de Boston"},
            "score": 2,
            "logo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
            "darkLogo": "https://assets.nhle.com/logos/nhl/svg/BOS_dark.svg",
        }
        team = TeamDetails(**team_data)
        assert team.id == 6
        assert team.abbrev == "BOS"
        assert team.score == 2

    def test_negative_score_rejected(self):
        """Test that negative scores are rejected."""
        team_data = {
            "id": 6,
            "abbrev": "BOS",
            "commonName": {"default": "Bruins"},
            "placeName": {"default": "Boston"},
            "placeNameWithPreposition": {"default": "Boston"},
            "score": -1,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamDetails(**team_data)
        assert "Score cannot be negative" in str(exc_info.value)

    def test_invalid_team_id(self):
        """Test that invalid team IDs are rejected."""
        team_data = {
            "id": 999,
            "abbrev": "XXX",
            "commonName": {"default": "Invalid"},
            "placeName": {"default": "Nowhere"},
            "placeNameWithPreposition": {"default": "Nowhere"},
            "score": 0,
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamDetails(**team_data)
        assert "Team ID out of valid range" in str(exc_info.value)


# ============================================================================
# Game Models Tests
# ============================================================================


class TestGame:
    """Test Game model."""

    def test_valid_game(self):
        """Test parsing valid game data."""
        game_data = {
            "id": 2024020761,
            "season": 20242025,
            "gameType": 2,
            "venue": {"default": "TD Garden"},
            "neutralSite": False,
            "startTimeUTC": "2025-01-24T00:00:00Z",
            "easternUTCOffset": "-05:00",
            "venueUTCOffset": "-05:00",
            "venueTimezone": "US/Eastern",
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "tvBroadcasts": [],
            "awayTeam": {
                "id": 9,
                "abbrev": "OTT",
                "commonName": {"default": "Senators"},
                "placeName": {"default": "Ottawa"},
                "placeNameWithPreposition": {"default": "Ottawa"},
                "score": 0,
            },
            "homeTeam": {
                "id": 6,
                "abbrev": "BOS",
                "commonName": {"default": "Bruins"},
                "placeName": {"default": "Boston"},
                "placeNameWithPreposition": {"default": "Boston"},
                "score": 2,
            },
            "periodDescriptor": {
                "number": 3,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "gameOutcome": {"lastPeriodType": "REG"},
        }
        game = Game(**game_data)
        assert game.id == 2024020761
        assert game.season == 20242025
        assert game.homeTeam.score == 2

    def test_invalid_datetime(self):
        """Test that invalid datetime is rejected."""
        game_data = {
            "id": 2024020761,
            "season": 20242025,
            "gameType": 2,
            "venue": {"default": "TD Garden"},
            "neutralSite": False,
            "startTimeUTC": "invalid-datetime",
            "easternUTCOffset": "-05:00",
            "venueUTCOffset": "-05:00",
            "venueTimezone": "US/Eastern",
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "tvBroadcasts": [],
            "awayTeam": {
                "id": 9,
                "abbrev": "OTT",
                "commonName": {"default": "Senators"},
                "placeName": {"default": "Ottawa"},
                "placeNameWithPreposition": {"default": "Ottawa"},
                "score": 0,
            },
            "homeTeam": {
                "id": 6,
                "abbrev": "BOS",
                "commonName": {"default": "Bruins"},
                "placeName": {"default": "Boston"},
                "placeNameWithPreposition": {"default": "Boston"},
                "score": 2,
            },
            "periodDescriptor": {
                "number": 3,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "gameOutcome": {"lastPeriodType": "REG"},
        }
        with pytest.raises(ValidationError) as exc_info:
            Game(**game_data)
        assert "Invalid ISO 8601 datetime" in str(exc_info.value)

    def test_invalid_season(self):
        """Test that invalid season format is rejected."""
        game_data = {
            "id": 2024020761,
            "season": 2025,  # Invalid: should be 8 digits
            "gameType": 2,
            "venue": {"default": "TD Garden"},
            "neutralSite": False,
            "startTimeUTC": "2025-01-24T00:00:00Z",
            "easternUTCOffset": "-05:00",
            "venueUTCOffset": "-05:00",
            "venueTimezone": "US/Eastern",
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "tvBroadcasts": [],
            "awayTeam": {
                "id": 9,
                "abbrev": "OTT",
                "commonName": {"default": "Senators"},
                "placeName": {"default": "Ottawa"},
                "placeNameWithPreposition": {"default": "Ottawa"},
                "score": 0,
            },
            "homeTeam": {
                "id": 6,
                "abbrev": "BOS",
                "commonName": {"default": "Bruins"},
                "placeName": {"default": "Boston"},
                "placeNameWithPreposition": {"default": "Boston"},
                "score": 2,
            },
            "periodDescriptor": {
                "number": 3,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "gameOutcome": {"lastPeriodType": "REG"},
        }
        with pytest.raises(ValidationError) as exc_info:
            Game(**game_data)
        assert "Invalid season format" in str(exc_info.value)

    def test_invalid_game_type(self):
        """Test that invalid game type is rejected."""
        game_data = {
            "id": 2024020761,
            "season": 20242025,
            "gameType": 99,  # Invalid game type
            "venue": {"default": "TD Garden"},
            "neutralSite": False,
            "startTimeUTC": "2025-01-24T00:00:00Z",
            "easternUTCOffset": "-05:00",
            "venueUTCOffset": "-05:00",
            "venueTimezone": "US/Eastern",
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "tvBroadcasts": [],
            "awayTeam": {
                "id": 9,
                "abbrev": "OTT",
                "commonName": {"default": "Senators"},
                "placeName": {"default": "Ottawa"},
                "placeNameWithPreposition": {"default": "Ottawa"},
                "score": 0,
            },
            "homeTeam": {
                "id": 6,
                "abbrev": "BOS",
                "commonName": {"default": "Bruins"},
                "placeName": {"default": "Boston"},
                "placeNameWithPreposition": {"default": "Boston"},
                "score": 2,
            },
            "periodDescriptor": {
                "number": 3,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "gameOutcome": {"lastPeriodType": "REG"},
        }
        with pytest.raises(ValidationError) as exc_info:
            Game(**game_data)
        assert "Invalid game type" in str(exc_info.value)


class TestGameDay:
    """Test GameDay model."""

    def test_valid_gameday(self):
        """Test parsing valid game day data."""
        gameday_data = {
            "date": "2025-01-23",
            "dayAbbrev": "THU",
            "numberOfGames": 1,
            "games": [
                {
                    "id": 2024020761,
                    "season": 20242025,
                    "gameType": 2,
                    "venue": {"default": "TD Garden"},
                    "neutralSite": False,
                    "startTimeUTC": "2025-01-24T00:00:00Z",
                    "easternUTCOffset": "-05:00",
                    "venueUTCOffset": "-05:00",
                    "venueTimezone": "US/Eastern",
                    "gameState": "OFF",
                    "gameScheduleState": "OK",
                    "tvBroadcasts": [],
                    "awayTeam": {
                        "id": 9,
                        "abbrev": "OTT",
                        "commonName": {"default": "Senators"},
                        "placeName": {"default": "Ottawa"},
                        "placeNameWithPreposition": {"default": "Ottawa"},
                        "score": 0,
                    },
                    "homeTeam": {
                        "id": 6,
                        "abbrev": "BOS",
                        "commonName": {"default": "Bruins"},
                        "placeName": {"default": "Boston"},
                        "placeNameWithPreposition": {"default": "Boston"},
                        "score": 2,
                    },
                    "periodDescriptor": {
                        "number": 3,
                        "periodType": "REG",
                        "maxRegulationPeriods": 3,
                    },
                    "gameOutcome": {"lastPeriodType": "REG"},
                }
            ],
        }
        gameday = GameDay(**gameday_data)
        assert gameday.date == "2025-01-23"
        assert gameday.numberOfGames == 1
        assert len(gameday.games) == 1

    def test_invalid_date_format(self):
        """Test that invalid date format is rejected."""
        gameday_data = {
            "date": "23-01-2025",  # Invalid format
            "dayAbbrev": "THU",
            "numberOfGames": 0,
            "games": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            GameDay(**gameday_data)
        assert "Invalid date format" in str(exc_info.value)


class TestGameScheduleResponse:
    """Test GameScheduleResponse model."""

    def test_valid_schedule_response(self):
        """Test parsing valid schedule response."""
        response_data = {
            "nextStartDate": "2025-01-30",
            "previousStartDate": "2025-01-16",
            "gameWeek": [
                {
                    "date": "2025-01-23",
                    "dayAbbrev": "THU",
                    "numberOfGames": 0,
                    "games": [],
                }
            ],
        }
        response = GameScheduleResponse(**response_data)
        assert response.nextStartDate == "2025-01-30"
        assert len(response.gameWeek) == 1


# ============================================================================
# Player Models Tests
# ============================================================================


class TestPlayerResponse:
    """Test PlayerResponse model."""

    def test_valid_player(self):
        """Test parsing valid player data."""
        player_data = {
            "firstName": {"default": "Nathan"},
            "lastName": {"default": "MacKinnon"},
            "sweaterNumber": 29,
            "position": "C",
        }
        player = PlayerResponse(**player_data)
        assert player.firstName.default == "Nathan"
        assert player.sweaterNumber == 29
        assert player.position == "C"

    def test_player_without_optional_fields(self):
        """Test parsing player without optional fields."""
        player_data = {
            "firstName": {"default": "Nathan"},
            "lastName": {"default": "MacKinnon"},
        }
        player = PlayerResponse(**player_data)
        assert player.sweaterNumber is None
        assert player.position is None

    def test_invalid_sweater_number(self):
        """Test that invalid sweater numbers are rejected."""
        player_data = {
            "firstName": {"default": "Nathan"},
            "lastName": {"default": "MacKinnon"},
            "sweaterNumber": 100,  # Invalid: too high
        }
        with pytest.raises(ValidationError) as exc_info:
            PlayerResponse(**player_data)
        assert "Invalid sweater number" in str(exc_info.value)

    def test_invalid_position(self):
        """Test that invalid position is rejected."""
        player_data = {
            "firstName": {"default": "Nathan"},
            "lastName": {"default": "MacKinnon"},
            "position": "X",  # Invalid position
        }
        with pytest.raises(ValidationError) as exc_info:
            PlayerResponse(**player_data)
        assert "Invalid position" in str(exc_info.value)


# ============================================================================
# Standings Models Tests
# ============================================================================


class TestStandingsResponse:
    """Test StandingsResponse model."""

    def test_valid_standings_entry(self):
        """Test parsing valid flat standings entry."""
        entry_data = {
            "teamName": {"default": "Boston Bruins"},
            "teamCommonName": {"default": "Bruins"},
            "teamAbbrev": {"default": "BOS"},
            "teamLogo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
            "placeName": {"default": "Boston"},
            "seasonId": 20242025,
            "conferenceAbbrev": "E",
            "conferenceName": "Eastern",
            "divisionAbbrev": "A",
            "divisionName": "Atlantic",
            "conferenceSequence": 2,
            "conferenceHomeSequence": 3,
            "conferenceRoadSequence": 1,
            "conferenceL10Sequence": 2,
            "divisionSequence": 1,
            "divisionHomeSequence": 2,
            "divisionRoadSequence": 1,
            "divisionL10Sequence": 2,
            "leagueSequence": 1,
            "leagueHomeSequence": 5,
            "leagueRoadSequence": 2,
            "leagueL10Sequence": 5,
            "waiversSequence": 31,
            "wildcardSequence": 0,
            "gamesPlayed": 50,
            "gameTypeId": 2,
            "date": "2024-02-07",
            "wins": 30,
            "losses": 15,
            "otLosses": 5,
            "ties": 0,
            "points": 65,
            "pointPctg": 0.65,
            "winPctg": 0.60,
            "regulationWins": 28,
            "regulationPlusOtWins": 33,
            "regulationWinPctg": 0.56,
            "regulationPlusOtWinPctg": 0.66,
            "goalFor": 160,
            "goalAgainst": 140,
            "goalDifferential": 20,
            "goalsForPctg": 3.2,
            "goalDifferentialPctg": 0.4,
            "homeGamesPlayed": 25,
            "homeWins": 18,
            "homeLosses": 5,
            "homeOtLosses": 2,
            "homeTies": 0,
            "homePoints": 38,
            "homeRegulationWins": 16,
            "homeRegulationPlusOtWins": 18,
            "homeGoalsFor": 85,
            "homeGoalsAgainst": 65,
            "homeGoalDifferential": 20,
            "roadGamesPlayed": 25,
            "roadWins": 12,
            "roadLosses": 10,
            "roadOtLosses": 3,
            "roadTies": 0,
            "roadPoints": 27,
            "roadRegulationWins": 12,
            "roadRegulationPlusOtWins": 15,
            "roadGoalsFor": 75,
            "roadGoalsAgainst": 75,
            "roadGoalDifferential": 0,
            "l10GamesPlayed": 10,
            "l10Wins": 7,
            "l10Losses": 2,
            "l10OtLosses": 1,
            "l10Ties": 0,
            "l10Points": 15,
            "l10RegulationWins": 6,
            "l10RegulationPlusOtWins": 7,
            "l10GoalsFor": 35,
            "l10GoalsAgainst": 25,
            "l10GoalDifferential": 10,
            "streakCode": "W",
            "streakCount": 2,
            "shootoutWins": 2,
            "shootoutLosses": 1,
        }
        entry = StandingsEntry(**entry_data)
        assert entry.teamAbbrev.default == "BOS"
        assert entry.conferenceName == "Eastern"
        assert entry.divisionName == "Atlantic"
        assert entry.points == 65

    def test_valid_standings_response(self):
        """Test parsing valid standings response with multiple teams."""
        standings_data = {
            "wildCardIndicator": True,
            "standings": [
                {
                    "teamName": {"default": "Boston Bruins"},
                    "teamCommonName": {"default": "Bruins"},
                    "teamAbbrev": {"default": "BOS"},
                    "teamLogo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
                    "placeName": {"default": "Boston"},
                    "seasonId": 20242025,
                    "conferenceAbbrev": "E",
                    "conferenceName": "Eastern",
                    "divisionAbbrev": "A",
                    "divisionName": "Atlantic",
                    "conferenceSequence": 2,
                    "conferenceHomeSequence": 3,
                    "conferenceRoadSequence": 1,
                    "conferenceL10Sequence": 2,
                    "divisionSequence": 1,
                    "divisionHomeSequence": 2,
                    "divisionRoadSequence": 1,
                    "divisionL10Sequence": 2,
                    "leagueSequence": 1,
                    "leagueHomeSequence": 5,
                    "leagueRoadSequence": 2,
                    "leagueL10Sequence": 5,
                    "waiversSequence": 31,
                    "wildcardSequence": 0,
                    "gamesPlayed": 50,
                    "gameTypeId": 2,
                    "date": "2024-02-07",
                    "wins": 30,
                    "losses": 15,
                    "otLosses": 5,
                    "ties": 0,
                    "points": 65,
                    "pointPctg": 0.65,
                    "winPctg": 0.60,
                    "regulationWins": 28,
                    "regulationPlusOtWins": 33,
                    "regulationWinPctg": 0.56,
                    "regulationPlusOtWinPctg": 0.66,
                    "goalFor": 160,
                    "goalAgainst": 140,
                    "goalDifferential": 20,
                    "goalsForPctg": 3.2,
                    "goalDifferentialPctg": 0.4,
                    "homeGamesPlayed": 25,
                    "homeWins": 18,
                    "homeLosses": 5,
                    "homeOtLosses": 2,
                    "homeTies": 0,
                    "homePoints": 38,
                    "homeRegulationWins": 16,
                    "homeRegulationPlusOtWins": 18,
                    "homeGoalsFor": 85,
                    "homeGoalsAgainst": 65,
                    "homeGoalDifferential": 20,
                    "roadGamesPlayed": 25,
                    "roadWins": 12,
                    "roadLosses": 10,
                    "roadOtLosses": 3,
                    "roadTies": 0,
                    "roadPoints": 27,
                    "roadRegulationWins": 12,
                    "roadRegulationPlusOtWins": 15,
                    "roadGoalsFor": 75,
                    "roadGoalsAgainst": 75,
                    "roadGoalDifferential": 0,
                    "l10GamesPlayed": 10,
                    "l10Wins": 7,
                    "l10Losses": 2,
                    "l10OtLosses": 1,
                    "l10Ties": 0,
                    "l10Points": 15,
                    "l10RegulationWins": 6,
                    "l10RegulationPlusOtWins": 7,
                    "l10GoalsFor": 35,
                    "l10GoalsAgainst": 25,
                    "l10GoalDifferential": 10,
                    "streakCode": "W",
                    "streakCount": 2,
                    "shootoutWins": 2,
                    "shootoutLosses": 1,
                }
            ],
        }
        standings = StandingsResponse(**standings_data)
        assert standings.wildCardIndicator is True
        assert len(standings.standings) == 1
        assert standings.standings[0].teamAbbrev.default == "BOS"

    def test_negative_record_values_rejected(self):
        """Test that negative record values are rejected."""
        entry_data = {
            "teamName": {"default": "Boston Bruins"},
            "teamCommonName": {"default": "Bruins"},
            "teamAbbrev": {"default": "BOS"},
            "placeName": {"default": "Boston"},
            "seasonId": 20242025,
            "conferenceAbbrev": "E",
            "conferenceName": "Eastern",
            "divisionAbbrev": "A",
            "divisionName": "Atlantic",
            "conferenceSequence": 2,
            "conferenceHomeSequence": 3,
            "conferenceRoadSequence": 1,
            "conferenceL10Sequence": 2,
            "divisionSequence": 1,
            "divisionHomeSequence": 2,
            "divisionRoadSequence": 1,
            "divisionL10Sequence": 2,
            "leagueSequence": 1,
            "leagueHomeSequence": 5,
            "leagueRoadSequence": 2,
            "leagueL10Sequence": 5,
            "waiversSequence": 31,
            "wildcardSequence": 0,
            "gamesPlayed": 50,
            "gameTypeId": 2,
            "date": "2024-02-07",
            "wins": -1,  # Invalid
            "losses": 15,
            "otLosses": 5,
            "ties": 0,
            "points": 65,
            "pointPctg": 0.65,
            "winPctg": 0.60,
            "regulationWins": 28,
            "regulationPlusOtWins": 33,
            "regulationWinPctg": 0.56,
            "regulationPlusOtWinPctg": 0.66,
            "goalFor": 160,
            "goalAgainst": 140,
            "goalDifferential": 20,
            "goalsForPctg": 3.2,
            "goalDifferentialPctg": 0.4,
            "homeGamesPlayed": 25,
            "homeWins": 18,
            "homeLosses": 5,
            "homeOtLosses": 2,
            "homeTies": 0,
            "homePoints": 38,
            "homeRegulationWins": 16,
            "homeRegulationPlusOtWins": 18,
            "homeGoalsFor": 85,
            "homeGoalsAgainst": 65,
            "homeGoalDifferential": 20,
            "roadGamesPlayed": 25,
            "roadWins": 12,
            "roadLosses": 10,
            "roadOtLosses": 3,
            "roadTies": 0,
            "roadPoints": 27,
            "roadRegulationWins": 12,
            "roadRegulationPlusOtWins": 15,
            "roadGoalsFor": 75,
            "roadGoalsAgainst": 75,
            "roadGoalDifferential": 0,
            "l10GamesPlayed": 10,
            "l10Wins": 7,
            "l10Losses": 2,
            "l10OtLosses": 1,
            "l10Ties": 0,
            "l10Points": 15,
            "l10RegulationWins": 6,
            "l10RegulationPlusOtWins": 7,
            "l10GoalsFor": 35,
            "l10GoalsAgainst": 25,
            "l10GoalDifferential": 10,
            "streakCode": "W",
            "streakCount": 2,
            "shootoutWins": 2,
            "shootoutLosses": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            StandingsEntry(**entry_data)
        assert "Record value cannot be negative" in str(exc_info.value)


# ============================================================================
# Roster Models Tests
# ============================================================================


class TestRosterResponse:
    """Test RosterResponse model."""

    def test_valid_roster(self):
        """Test parsing valid roster data."""
        roster_data = {
            "season": 20242025,
            "forwards": [
                {
                    "id": 8470601,
                    "firstName": {"default": "Nathan"},
                    "lastName": {"default": "MacKinnon"},
                    "sweaterNumber": 29,
                    "position": "C",
                    "status": "A",
                }
            ],
            "defensemen": [
                {
                    "id": 8470150,
                    "firstName": {"default": "Cale"},
                    "lastName": {"default": "Makar"},
                    "sweaterNumber": 8,
                    "position": "D",
                    "status": "A",
                }
            ],
            "goalies": [
                {
                    "id": 8471735,
                    "firstName": {"default": "Pavel"},
                    "lastName": {"default": "Zacha"},
                    "sweaterNumber": 37,
                    "position": "G",
                    "status": "A",
                }
            ],
        }
        roster = RosterResponse(**roster_data)
        assert roster.season == 20242025
        assert len(roster.forwards) == 1
        assert roster.forwards[0].position == "C"
        assert roster.defensemen[0].position == "D"
        assert roster.goalies[0].position == "G"

    def test_invalid_player_position_in_roster(self):
        """Test that invalid player position in roster is rejected."""
        roster_data = {
            "season": 20242025,
            "forwards": [
                {
                    "id": 8470601,
                    "firstName": {"default": "Nathan"},
                    "lastName": {"default": "MacKinnon"},
                    "sweaterNumber": 29,
                    "position": "X",  # Invalid
                    "status": "A",
                }
            ],
            "defensemen": [],
            "goalies": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            RosterResponse(**roster_data)
        assert "Invalid position" in str(exc_info.value)
