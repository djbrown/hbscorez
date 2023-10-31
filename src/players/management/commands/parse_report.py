import logging

from base import logic, parsing
from games.models import Game
from players.models import Player, Score
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


def parse_spectators(table) -> int | None:
    specs: str = table['data'][4][2]['text']
    if specs == 'k.A.':
        return None

    try:
        return int(specs)
    except ValueError:
        return None


def import_score(table_row, game: Game, team: Team):
    row_data = [cell['text'] for cell in table_row]

    player_number: str = row_data[0]
    player_name: str = row_data[1].split("(", 1)[0].strip()

    if not player_number and not player_name:
        return
    if player_number in ('A', 'B', 'C', 'D'):
        LOGGER.debug('SKIPPING Score (coach): %s - %s', player_number, player_name)
        return
    if not player_number:
        LOGGER.warning('SKIPPING Score (no player number): %s', player_name)
        return
    if not player_name:
        LOGGER.warning('SKIPPING Score (no player name): %s', player_number)
        return
    try:
        int(player_number)
    except ValueError as err:
        LOGGER.exception('invalid Score (invalid player number): %s - %s\n%s', player_number, player_name, err)
        return

    player = Player(name=player_name, team=team)
    score = parse_score(player, game, row_data)
    logic.add_score(score)


def parse_score(player: Player, game: Game, row_data) -> Score:
    player_number = int(row_data[0])
    goals_str = row_data[5]
    if goals_str == '':
        goals = 0
    else:
        try:
            goals = int(goals_str)
        except ValueError as err:
            goals = 0
            LOGGER.exception('invalid Score goals: %s - %s - %s\n%s', player_number, player.name, goals, err)
    penalty_tries, penalty_goals = parsing.parse_penalty_data(row_data[6])

    return Score(player=player, player_number=int(row_data[0]), game=game, goals=goals,
                 penalty_tries=penalty_tries, penalty_goals=penalty_goals,
                 warning_time=parsing.parse_game_time(row_data[7]),
                 first_suspension_time=parsing.parse_game_time(row_data[8]),
                 second_suspension_time=parsing.parse_game_time(row_data[9]),
                 third_suspension_time=parsing.parse_game_time(row_data[10]),
                 disqualification_time=parsing.parse_game_time(row_data[11]),
                 report_time=parsing.parse_game_time(row_data[12]),
                 team_suspension_time=parsing.parse_game_time(row_data[13]))
