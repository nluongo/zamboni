from zamboni.db_con import DBConnector
from datetime import date

def days_games(days_date=date.today()):
    db_connector = DBConnector()
    db_con = db_connector.connect_db()

    year, month, day = days_date.split('-')
    query_sql = f'''SELECT home_teams.nameAbbrev,
                            games.homeTeamGoals,
                            away_teams.nameAbbrev,
                            games.awayTeamGoals
                    FROM games 
                    LEFT OUTER JOIN teams home_teams ON games.homeTeamID = home_teams.id
                    LEFT OUTER JOIN teams away_teams ON games.awayTeamID = away_teams.id
                    WHERE datePlayed="{days_date}"'''
    with db_con as cursor:
        query_res = cursor.execute(query_sql)
        games = query_res.fetchall()

    return games

if __name__ == '__main__':
    days_games('2025-02-09')
