import pytest
from zamboni import APICaller

error_message = 'The API output has changed'

def test_player():
    caller = APICaller('player')
    test_id = 8447400
    out = caller.query([test_id])
    assert out['firstName']['default'] == 'Wayne' and out['lastName']['default'] == 'Gretzky', error_message

def test_game():
    from datetime import date
    caller = APICaller('game')
    test_date = date(1997, 3, 26)
    out = caller.query([test_date])
    assert 'gameWeek' in out
    week = out['gameWeek']
    found_day = False
    for day in week:
        if day['date'] == '1997-03-26':
            game_day = day
            found_day = True
    assert found_day
    found_game = False
    for game in game_day['games']:
        if game['venue']['default'] == 'Joe Louis Arena':
            test_game = game
            found_game = True
    assert test_game['homeTeam']['placeName']['default'] == 'Detroit' and test_game['homeTeam']['score'] == 6
    assert test_game['awayTeam']['placeName']['default'] == 'Colorado' and test_game['awayTeam']['score'] == 5
