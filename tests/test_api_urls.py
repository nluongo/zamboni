from zamboni import APICaller


def test_url_base():
    url_base = APICaller.url_base
    assert url_base == "https://api-web.nhle.com/v1/"


def test_standings_url():
    caller = APICaller()
    caller.set_url_template("standings")
    url = caller.url
    assert url == "https://api-web.nhle.com/v1/standings/{}"


def test_player_url():
    caller = APICaller()
    caller.set_url_template("player")
    url = caller.url
    assert url == "https://api-web.nhle.com/v1/player/{}/landing"


def test_game_url():
    caller = APICaller()
    caller.set_url_template("game")
    url = caller.url
    assert url == "https://api-web.nhle.com/v1/schedule/{}"


def test_roster_url():
    caller = APICaller()
    caller.set_url_template("roster")
    url = caller.url
    assert url == "https://api-web.nhle.com/v1/roster/{}/{}{}"
