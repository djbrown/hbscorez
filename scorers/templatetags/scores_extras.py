from django.contrib.staticfiles.templatetags.staticfiles import static

from scorers.models import Club


def dec(value, arg):
    return value - arg


def place(scorers: list, index: int) -> int:
    goals = scorers[index].total_goals
    while index > 0 and goals == scorers[index - 1].total_goals:
        index -= 1
    return index + 1


def club_logo_url(club: Club):
    if club.logo:
        return club.logo.url
    else:
        return static('base/images/favicons/favicon.png')
