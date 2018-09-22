from datetime import datetime, timedelta

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from icalendar import Calendar, Event, vText

from base.logic import add_ranking_place
from games.models import Game, TeamOutcome
from players.models import Player
from teams.models import Team


def detail(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    return render(request, 'teams/detail.j2', {'team': team})


def games(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team)).order_by('opening_whistle')
    return render(request, 'teams/games.j2', {'team': team, 'games': games})


def scorers(request, bhv_id):
    # todo: change view to show portraits and summary data of the players (not scorers data)
    team = get_object_or_404(Team, bhv_id=bhv_id)
    players = Player.objects \
        .filter(team=team) \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Coalesce(Sum('score__goals'), 0)) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .annotate(total_field_goals=F('total_goals') - F('total_penalty_goals')) \
        .order_by('-total_goals')
    add_ranking_place(players, 'total_goals')
    return render(request, 'teams/scorers.j2', {'team': team, 'players': players})


def offenders(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_offenders = Player.objects \
        .filter(team=team) \
        .annotate(games=Count('score')) \
        .annotate(warnings=Count('score__warning_time')) \
        .annotate(suspensions=Count('score__first_suspension_time') +
                  Count('score__second_suspension_time') +
                  Count('score__third_suspension_time')) \
        .annotate(disqualifications=Count('score__disqualification_time')) \
        .annotate(offender_points=F('warnings') + 2 * F('suspensions') + 3 * F('disqualifications')) \
        .order_by('-offender_points')
    add_ranking_place(team_offenders, 'offender_points')
    return render(request, 'teams/offenders.j2', {'team': team, 'offenders': team_offenders})


def calendar(_, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team))

    cal = Calendar()
    cal.add('PRODID', '-//HbScorez//Mannschaftskalender 1.0//DE')
    cal.add('VERSION', '2.0')
    cal.add('CALSCALE', 'GREGORIAN')
    cal.add('METHOD', 'PUBLISH')
    cal.add('X-WR-CALNAME', 'Spielplan {} {}'.format(team.league.abbreviation, team.short_name))
    cal.add('X-WR-TIMEZONE', 'Europe/Berlin')
    cal.add('X-WR-CALDESC', 'Spielplan der Mannschaft "{}" in der Saison {}/{} in der Liga "{}" des Bereichs "{}"'
            .format(team.name, team.league.season.start_year, team.league.season.start_year + 1,
                    team.league.name, team.league.district.name))

    for game in games:
        cal.add_component(_create_event(team, game))

    return HttpResponse(cal.to_ical(), "text/calendar")


def _create_event(team, game):
    event = Event()

    venue = 'Heimspiel' if game.home_team == team else 'Auswärtsspiel'
    summary = '{} - {}'.format(venue, game.opponent_of(team).short_name)
    leg = 'Hinspiel' if game.is_first_leg() else 'Rückspiel'
    description = '{} gegen {}'.format(leg, game.opponent_of(team).name)
    if not game.is_first_leg():
        previous = game.other_game()
        description += '\nHinspiel: {}:{} ({})'.format(previous.home_goals, previous.guest_goals, _outcome(game, team))
    start = game.opening_whistle
    end = start + timedelta(minutes=90)
    dtstamp = datetime.now()
    # todo: read location from game.sports_halls / game.location
    location = game.sports_hall.address
    uid = 'game/{}@hbscorez.de'.format(game.number)

    event.add('summary', summary)
    event.add('description', description)
    event.add('dtstart', start)
    event.add('dtend', end)
    event.add('dtstamp', dtstamp)
    event['location'] = vText(location)
    event['uid'] = uid
    return event


def _outcome(game, team):
    mapping = {
        TeamOutcome.WIN: 'Sieg',
        TeamOutcome.LOSS: 'Niederlage',
        TeamOutcome.TIE: 'Unentschieden',
    }
    o = game.outcome_for(team)
    return mapping.get(o)


def _display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()
