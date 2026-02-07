from zamboni import APICaller
from zamboni.api_caller import NHLAPIValidationError
from zamboni.utils import zero_pad
from datetime import datetime, date, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)
today_date = date.today()


def query_date_games(caller, in_date):
    """
    Query NHL API for games on a specific date.

    :param caller: APICaller instance
    :param in_date: Date to query for
    :returns: GameScheduleResponse model or None if error occurs
    """
    year_str = zero_pad(in_date.year, 4)
    month_str = zero_pad(in_date.month, 2)
    day_str = zero_pad(in_date.day, 2)
    date_string = f"{year_str}-{month_str}-{day_str}"
    logger.info(f"Querying API at date {date_string}")
    try:
        response = caller.query([date_string], "game", throw_error=False)
        return response
    except NHLAPIValidationError as e:
        logger.error(f"Validation error querying games for {date_string}: {e}")
        return None


def write_game_data(f, game, completed=True):
    """
    Write game data to file using Game Pydantic model.

    :param f: File object to write to
    :param game: Game Pydantic model
    :param completed: Whether game is completed
    """
    try:
        api_id = game.id
        season_id = game.season
        datetime_utc = datetime.fromisoformat(game.startTimeUTC.replace("Z", "+00:00"))
        timezone_offset = game.venueUTCOffset
        hour_offset, minute_offset = timezone_offset.split(":")
        offset = timedelta(hours=int(hour_offset), minutes=int(minute_offset))
        datetime_local = datetime_utc + offset
        day_of_yr = datetime_local.timetuple().tm_yday
        year = datetime_local.year
        home_id = game.homeTeam.id
        home_abbrev = game.homeTeam.abbrev
        away_id = game.awayTeam.id
        away_abbrev = game.awayTeam.abbrev
        type_id = game.gameType
        home_goals = getattr(game.homeTeam, "score", None)
        away_goals = getattr(game.awayTeam, "score", None)
        game_outcome = getattr(game, "gameOutcome", None)
        if game_outcome:
            last_period_type = getattr(game, "lastPeriodType", None)
        if not (home_goals and away_goals and game_outcome and last_period_type):
            home_goals = ""
            away_goals = ""
            last_period_type = ""
    except (AttributeError, ValueError) as e:
        logger.warning(f"Error extracting game data: {e}")
        return

    game_string = f"{api_id}, {season_id}, {home_id}, {home_abbrev}, {away_id}, {away_abbrev}, {datetime_local.date()}, {day_of_yr}, {year}, {datetime_local.time()}, {home_goals}, {away_goals}, {type_id}, {last_period_type}\n"
    f.write(game_string)


def write_game_data_all(f, game, first_line=False):
    """
    Flattens the game dictionary completely and writes the keys in the first line
    and the values in subsequent lines.
    """

    def flatten_dict(d, parent_key="", sep="."):
        """Recursively flattens a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings to preserve structure
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    try:
        # Flatten the game dictionary
        flattened_game = flatten_dict(game)

        # Write the keys in the first line
        if first_line:
            keys = ", ".join(flattened_game.keys())
            f.write(keys + "\n")

        # Write the values in the subsequent lines
        values = ", ".join(map(str, flattened_game.values()))
        f.write(values + "\n")
    except Exception as e:
        logger.error(f"Error flattening or writing game data: {e}")


def download_games(start_year=2024, out_path="data/games.txt", all=False):
    """
    Download NHL game data from API and write to file.

    :param start_year: Year to start downloading from
    :param out_path: Path to output file
    :param all: If True, write all fields; if False, write subset
    """
    caller = APICaller()

    # Date chosen to capture preseason
    start_date, sched_date = date(start_year, 9, 1), date(start_year, 9, 1) 
    day_delta = timedelta(days=1)

    # Download up to previous day and load to main file
    with open(out_path, "a+") as f:
        f.seek(0)
        lines = f.readlines()
        first_line = len(lines) == 0

        # Start at date of latest game in file
        if len(lines) > 0:
            for line in lines:
                pass
            last_line = line
            game_date = last_line.split(",")[6].strip()
            last_date = datetime.fromisoformat(game_date).date()
            sched_date = last_date + day_delta
            logger.info(f"Starting download at date {sched_date}")
        else:
            logger.info("No games downloaded, starting at the beginning..")

        while sched_date < today_date:
            response = query_date_games(caller, sched_date)
            if not response:
                sched_date += day_delta
                continue

            for day in response.gameWeek:
                if not day.games:
                    logger.info(f"No games found for date {day.date}")
                    sched_date += day_delta
                    continue

                for game in day.games:
                    if all:
                        # Convert Pydantic model to dict for flattening
                        game_dict = game.model_dump()
                        write_game_data_all(f, game_dict, first_line)
                        first_line = False
                    else:
                        write_game_data(f, game)
                sched_date += day_delta

    # Download current day and load into separate file
    with open("data/games_today.txt", "w") as f:
        response = query_date_games(caller, today_date)
        if not response:
            logger.info(f"No games found for date {today_date}")
            return

        for day in response.gameWeek:
            if day.date != str(today_date):
                continue
            if not day.games:
                logger.info(f"No games found for date {day.date}")
                continue
            for game in day.games:
                write_game_data(f, game, completed=False)

    # Download full schedule through the end of latest season
    current_year = today_date.year
    if today_date > date(current_year, 7, 1):
        end_date = date(current_year + 1, 7, 1)
    else:
        end_date = date(current_year, 7, 1)
    sched_date = start_date

    with open("data/games_all.txt", "a+") as f:
        f.seek(0)
        lines = f.readlines()
        first_line = len(lines) == 0

        # Start at date of latest game in file
        if len(lines) > 0:
            for line in lines:
                pass
            last_line = line
            game_date = last_line.split(",")[6].strip()
            last_date = datetime.fromisoformat(game_date).date()
            sched_date = last_date + day_delta
            logger.info(f"Starting download at date {sched_date}")
        else:
            logger.info("No games downloaded, starting at the beginning..")

        while sched_date < end_date:
            response = query_date_games(caller, sched_date)
            if not response:
                logger.info(f"No games found for date {today_date}")
                return

            for day in response.gameWeek:
                for game in day.games:
                    write_game_data(f, game, completed=False)

            sched_date += day_delta


def download_players(out_path="data/players.txt"):
    caller = APICaller()

    # api_id = 8475104
    api_id = 8440000
    # Less than 2500 players in the league
    # end_id = 8477604
    end_id = 8500000
    step = 1
    with open("data/players.txt", "w") as f:
        while api_id < end_id:
            player = caller.query([api_id], "player", throw_error=False)
            if not player:
                if api_id % step == 0:
                    print(api_id)
                api_id += 1
                continue
            first_name = player["firstName"]["default"]
            last_name = player["lastName"]["default"]
            full_name = f"{first_name} {last_name}"
            if "sweaterNumber" not in player.keys():
                number = "-1"
            else:
                number = str(player["sweaterNumber"])
            if "position" not in player.keys():
                position = "U"
            else:
                position = player["position"]
            write_string = ",".join(
                [str(api_id), full_name, first_name, last_name, number, position]
            )
            f.write(write_string + "\n")
            api_id += 1


def download_rosters(start_year=2024, out_path="data/rosterEntries.txt"):
    from datetime import datetime

    caller = APICaller()

    with open("data/teams.txt", "r") as f_teams:
        team_lines = f_teams.readlines()
        team_lines = [line.split(",") for line in team_lines]
        team_abbrevs = [line[1].strip() for line in team_lines]

    end_year = start_year + 1

    with open("data/rosterEntries.txt", "a") as roster_f:
        while start_year < datetime.now().year:
            end_year = start_year + 1
            logger.info(f"Querying API for {start_year}-{end_year} season rosters")
            for team in team_abbrevs:
                api_ids = [team, start_year, end_year]
                out = caller.query(api_ids, "roster", throw_error=False)
                if out is None:
                    continue
                forwards = out["forwards"]
                defensemen = out["defensemen"]
                goalies = out["goalies"]
                players = forwards + defensemen + goalies
                for player in players:
                    first_name = player["firstName"]["default"]
                    last_name = player["lastName"]["default"]
                    api_id = player["id"]
                    entry_str = f"{api_id}, {team}, {start_year}, {first_name}, {last_name}, {start_year}, {end_year}\n"
                    roster_f.write(entry_str)
            start_year += 1


def download_teams(start_year=2024, out_path="data/teams.txt"):
    """
    Download team information from NHL API standings endpoint.

    :param start_year: Year to start downloading from
    :param out_path: Path to output file
    """

    caller = APICaller()
    query_year = start_year
    cur_year = today_date.year
    teams_to_write = set()

    while query_year <= cur_year:
        query_date = f"{query_year}-12-31"
        logger.info(
            f"Querying API for teams during {query_year}-{query_year + 1} season"
        )
        response = caller.query([query_date], "standings")

        if not response:
            logger.warning(f"Failed to get standings for {query_date}")
            query_year += 1
            continue

        for team in response.standings:
            team_name = team.teamName.default
            team_abbrev = team.teamAbbrev.default

            # Special case skipping Utah Hockey Club, which was renamed to Mammoth
            if team_name == "Utah Hockey Club":
                continue
            if not team_name or not team_abbrev:
                continue

            conf_abbrev = team.conferenceAbbrev
            div_abbrev = team.divisionAbbrev
            team_str = f"{team_name}, {team_abbrev}, {conf_abbrev}, {div_abbrev}\n"
            teams_to_write.add(team_str)
        query_year += 1

    with open("data/teams.txt", "w") as f:
        for team_str in sorted(list(teams_to_write)):
            f.write(team_str)


def download_seasons(start_year):
    """
    Download NHL season data from API and write to file.

    :param out_path: Path to output file
    """
    # Don't actually need to download as we know what the records are
    begin_year = start_year

    with open("data/seasons.txt", "w") as f:
        i = 0
        while begin_year < today_date.year:
            api_id = begin_year * 10001 + 1
            start_year = begin_year
            end_year = begin_year + 1
            season_str = f"{api_id}, {start_year}, {end_year}\n"
            logger.debug(f"Writing season: {season_str.strip()}")
            f.write(season_str)
            begin_year += 1
            if i > 100:
                break
            i += 1


def main(start_year=2023):
    download_dir = "data"
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    download_seasons(start_year=start_year)
    download_teams(start_year=start_year)
    download_games(start_year=start_year)
    # download_players()
    # download_rosters(start_year=start_year)


if __name__ == "__main__":
    main()
