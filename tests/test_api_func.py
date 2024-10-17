import pytest
from zamboni import APICaller

def test_url_base():
    url_base = APICaller.url_base
    assert url_base == 'https://api-web.nhle.com/v1/'

def test_standings_url():
    caller = APICaller('standings')
    url = caller.url
    assert url == 'https://api-web.nhle.com/v1/standings/now'

def test_player_url():
    caller = APICaller('player')
    url = caller.url
    assert url == 'https://api-web.nhle.com/v1/player/{}/landing'

def test_game_url():
    caller = APICaller('game')
    url = caller.url
    assert url == 'https://api-web.nhle.com/v1/schedule/{}'

def test_roster_url():
    caller = APICaller('roster')
    url = caller.url
    assert url == 'https://api-web.nhle.com/v1/roster/{}/{}{}'
