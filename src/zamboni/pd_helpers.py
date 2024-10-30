import pandas as pd
import numpy as np

def filter_by_game_type(df, type_id):
    type_mask = df['gameTypeID'] == type_id
    return df[type_mask]

def filter_by_season(df, season_id):
    season_mask = df['seasonID'] == season_id
    return df[season_mask]

def filter_by_team(df, team_id):
    mask = np.any([df['homeTeamID'] == team_id, df['awayTeamID'] == team_id], axis=0)
    return df[mask]

def won_by_team(df, team_id):
    is_home_team_mask = df['homeTeamID'] == team_id
    home_team_wins_mask = df['homeTeamGoals'] > df['awayTeamGoals']
    is_away_team_mask = df['awayTeamID'] == team_id
    away_team_wins_mask = df['homeTeamGoals'] < df['awayTeamGoals']
    home_and_wins_mask = np.all([is_home_team_mask, home_team_wins_mask], axis=0)
    away_and_wins_mask = np.all([is_away_team_mask, away_team_wins_mask], axis=0)
    wins_mask = np.any([home_and_wins_mask, away_and_wins_mask], axis=0)
    return df[wins_mask]

def _wins_game(row, team_id):
    is_home_mask = row['homeTeamID'] == team_id
    home_win_mask = row['homeTeamGoals'] > row['awayTeamGoals']
    home_and_win_mask = np.all([is_home_mask, home_win_mask])
    is_away_mask = row['awayTeamID'] == team_id
    away_win_mask = row['homeTeamGoals'] < row['awayTeamGoals']
    away_and_win_mask = np.all([is_away_mask, away_win_mask])
    win_mask = np.any([home_and_win_mask, away_and_win_mask])
    if win_mask:
        return True
    else:
        return False
