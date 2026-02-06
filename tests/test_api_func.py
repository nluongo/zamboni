from zamboni import APICaller
from zamboni.nhl_models import (
    GameDay,
    GameScheduleResponse,
    StandingsResponse,
    PlayerResponse,
    Game,
    RosterResponse,
)


def test_url_base():
    url_base = APICaller.url_base
    assert url_base == "https://api-web.nhle.com/v1/"


def test_standings_model():
    caller = APICaller()
    caller.set_url_template("standings")
    out = caller.query(record_ids=[20232024], record_type="standings")
    assert isinstance(out, StandingsResponse)


def test_player_url():
    caller = APICaller()
    caller.set_url_template("player")
    out = caller.query(record_ids=[8478402], record_type="player")
    assert isinstance(out, PlayerResponse)


def test_game_url():
    caller = APICaller()
    caller.set_url_template("game")
    out = caller.query(record_ids=["2025-01-24"], record_type="game")
    assert (
        isinstance(out, GameScheduleResponse)
        and isinstance(out.gameWeek[0], GameDay)
        and isinstance(out.gameWeek[0].games[0], Game)
    )


def test_roster_url():
    caller = APICaller()
    caller.set_url_template("roster")
    out = caller.query(record_ids=[8478402, 20232024, "A"], record_type="roster")
    assert isinstance(out, RosterResponse)
