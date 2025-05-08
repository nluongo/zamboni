from collections import defaultdict
import csv
import logging
from zamboni.utils import split_csv_line

logger = logging.getLogger(__name__)

class TeamService:
    ''' Service to get team data '''
    def __init__(self, db_con):
        self.db_con = db_con
        self.abbrev_id_dict = defaultdict(lambda: -1)
        self.id_abbrev_dict = defaultdict(lambda: 'N/A')

    def build_abbrev_id_dicts(self):
        ''' Build a dictionary of team abbreviations to IDs '''
        with self.db_con as con:
            cursor = con.execute('SELECT id, nameAbbrev FROM teams')
            rows = cursor.fetchall()
            for row in rows:
                team_id, abbrev = row
                self.abbrev_id_dict[abbrev] = team_id
                self.id_abbrev_dict[team_id] = abbrev

    def id_from_abbrev(self, abbrev):
        team_id = self.abbrev_id_dict[abbrev]
        if team_id == -1:
            logging.warning(f'ID for team with abbreviation {abbrev} not found')
        return team_id

    def abbrev_from_id(self, team_id):
        if self.abbrev_id_dict == defaultdict(lambda: -1):
            self.build_abbrev_id_dicts()
        abbrev = self.id_abbrev_dict[team_id]
        if abbrev == 'N/A':
            logging.warning(f'Abbreviation for team with ID {team_id} not found')
        return abbrev

class Team:
    ''' One team, defined by ID or abbreviation '''
    def __str__(self):
        return f'{self.full_name} ({self.abbrev}) with ID {self.id}'
    def __repr__(self):
        return f'{self.__class__.__name__}({self.abbrev})'

    @classmethod
    def from_csv_line(cls, line):
        line = split_csv_line(line)
        team = Team(line[1])
        team.full_name = line[0]
        team.conf_abbrev = line[2]
        team.div_abbrev = line[3]

    def __init__(self, abbrev):
        self.abbrev = abbrev

class Game:
    ''' One game, defined by home team, away team and date '''
    def __str__(self):
        return f'{self.home_abbrev} vs {self.away_abbrev} on {self.date}'
    def __repr__(self):
        return f'{self.__class__.__name__}({self.home_abbrev}, {self.away_abbrev}, {self.date})'
    def __eq__(self, other):
        return (self.home_abbrev == other.home_abbrev and
                self.away_abbrev == other.away_abbrev and
                self.date == other.date)

    @classmethod
    def from_csv_line(self, line):
        line = split_csv_line(line)
        game = Game(line[3], line[5], line[6])
        game.api_id = line[0]
        game.season_id = line[1]
        game.date_played = line[6]
        game.day_of_year_played = line[7]
        game.year_played = line[8]
        game.time_played = line[9]
        game.home_team_goals = line[10]
        game.away_team_goals = line[11]
        game.game_type_id = line[12]
        game.last_period_type_id = line[13]
        return game

    def __init__(self, home_abbrev, away_abbrev, date):
        self.home_abbrev = home_abbrev
        self.away_abbrev = away_abbrev
        self.date = date

    @property
    def completed(self):
        ''' Check if game is completed '''
        return 1 if self.home_team_goals and self.away_team_goals else 0

    @property
    def outcome(self):
        ''' Get outcome of game '''
        if not self.completed:
            return -1
        elif self.home_team_goals > self.away_team_goals:
            return 1
        elif self.home_team_goals < self.away_team_goals:
            return 0
        else:
            logging.warning(f'Game {self} ended in a tie, which is not usually possible')
            return -1

    @property
    def in_ot(self):
        ''' Check if game went to overtime '''
        if not self.completed:
            return -1
        if self.game_type_id == 'REG':
            return 0
        else:
            return 1

    def team_ids_from_abbrev(self, team_service):
        ''' Get team IDs from abbreviations '''
        self.home_team_id = team_service.id_from_abbrev(self.home_abbrev)
        self.away_team_id = team_service.id_from_abbrev(self.away_abbrev)
        if self.home_team_id == -1:
            logging.warning(f'ID for home team {self.home_abbrev} not found')
        if self.away_team_id == -1:
            logging.warning(f'ID for away team {self.away_abbrev} not found')
