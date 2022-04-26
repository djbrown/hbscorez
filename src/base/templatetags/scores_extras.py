from django.templatetags.static import static

from games.models import GameOutcome, TeamOutcome
from teams.models import Team


def dec(value, arg):
    return value - arg


def team_logo_url(team: Team):
    if team.logo:
        return team.logo.url

    return static('base/images/favicons/favicon.png')


def team_outcome_badge(outcome: TeamOutcome):
    if outcome is TeamOutcome.OPEN:
        return "-"

    mapping = {
        TeamOutcome.WIN: ('success', 'Sieg'),
        TeamOutcome.TIE: ('warning', 'Unentschieden'),
        TeamOutcome.LOSS: ('danger', 'Niederlage')
    }
    return f'<span class="badge bg-{mapping[outcome][0]}">{mapping[outcome][1]}</span>'


def game_outcome_badge(outcome: GameOutcome):
    if outcome is GameOutcome.OPEN:
        return "-"

    mapping = {
        GameOutcome.HOME_WIN: 'Heimsieg',
        GameOutcome.AWAY_WIN: 'Auswärtssieg',
        GameOutcome.TIE: 'Unentschieden',
    }
    return f'<span class="badge bg-secondary">{mapping[outcome]}</span>'
