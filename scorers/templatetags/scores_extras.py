from django.contrib.staticfiles.templatetags.staticfiles import static

from scorers.models import Team


def dec(value, arg):
    return value - arg


def place(scorers: list, index: int) -> int:
    goals = scorers[index].total_goals
    while index > 0 and goals == scorers[index - 1].total_goals:
        index -= 1
    return index + 1


def team_logo_url(team: Team):
    if team.logo:
        return team.logo.url
    else:
        return static('base/images/favicons/favicon.png')
