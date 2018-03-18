from django.contrib.staticfiles.templatetags.staticfiles import static

from base import models


def dec(value, arg):
    return value - arg


def place(players: list, index: int) -> int:
    goals = players[index].total_goals
    while index > 0 and goals == players[index - 1].total_goals:
        index -= 1
    return index + 1


def team_logo_url(team: models.Team):
    if team.logo:
        return team.logo.url
    else:
        return static('base/images/favicons/favicon.png')


def team_outcome_badge(outcome: models.TeamOutCome):
    if outcome is None:
        return "-"

    mapping = {
        models.TeamOutCome.WIN: ('success', 'Sieg'),
        models.TeamOutCome.TIE: ('warning', 'Unentschieden'),
        models.TeamOutCome.LOSS: ('danger', 'Niederlage')
    }
    return '<span class="badge badge-{}">{}</span>'.format(*mapping[outcome])


def game_outcome_badge(outcome: models.GameOutcome):
    if outcome is None:
        return "-"

    mapping = {
        models.GameOutcome.HOME_WIN: 'Heimsieg',
        models.GameOutcome.AWAY_WIN: 'Auswärtssieg',
        models.GameOutcome.TIE: 'Unentschieden',
    }
    return '<span class="badge badge-light">{}</span>'.format(mapping[outcome])
