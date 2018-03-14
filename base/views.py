from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from icalendar import Calendar, Event, vText

from base.models import *


def view_home(request):
    return render(request, 'base/home.html')


def view_notice(request):
    return render(request, 'base/notice.html')


def view_contact(request):
    return render(request, 'base/contact.html')


def view_associations(request):
    associations = Association.objects.all()
    return render(request, 'base/associations.html', {'associations': associations})


def view_association(request, bhv_id):
    association = get_object_or_404(Association, bhv_id=bhv_id)
    return render(request, 'base/association.html', {'association': association})


def view_district(request, bhv_id):
    district = get_object_or_404(District, bhv_id=bhv_id)
    return render(request, 'base/district.html', {'district': district})


def view_league(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    return render(request, 'base/league.html', {'league': league})


def view_league_players(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    teams = Team.objects.filter(league=league)
    players = Player.objects \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .filter(total_goals__gt=0) \
        .filter(team__in=teams) \
        .order_by('-total_goals')
    return render(request, 'base/league_players.html', {'league': league, 'players': players})


def view_team(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    players = Player.objects \
        .filter(team=team) \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .order_by('-total_goals')
    return render(request, 'base/team.html', {'team': team, 'players': players})


def view_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    scores = Score.objects.filter(player=player)
    return render(request, 'base/player.html', {'player': player, 'scores': scores})


def view_team_games(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team))
    return render(request, 'base/team_games.html', {'team': team, 'games': games})


def view_team_calendar(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team))

    cal = Calendar()
    cal.add('PRODID', '-//hbscorez.de//Mannschaftskalender 1.0//DE')
    cal.add('VERSION', '2.0')
    cal.add('CALSCALE', 'GREGORIAN')
    cal.add('METHOD', 'PUBLISH')
    cal.add('X-WR-CALNAME', 'Spielplan {} {}'.format(team.league.abbreviation, team.short_name))
    cal.add('X-WR-TIMEZONE', 'Europe/Berlin')
    cal.add('X-WR-CALDESC', 'Spielplan der Mannschaft "{}" in der Saison 2018 in der Liga "{}" des Bereichs "{}"'
            .format(team.name, team.league.name, team.league.district.name))

    [cal.add_component(create_event(team, game)) for game in games]

    return HttpResponse(cal.to_ical(), "text/calendar")


def create_event(team, game):
    event = Event()

    venue = 'Heimspiel' if game.home_team == team else 'Auswärtsspiel'
    summary = '{} - {}'.format(venue, game.opponent_of(team).short_name)
    leg = 'Hinspiel' if game.is_first_leg() else 'Rückspiel'
    description = '{} gegen {}'.format(leg, game.opponent_of(team).name)
    if not game.is_first_leg():
        previous = game.other_game()
        description += '\nHinspiel: {}:{} ({})'.format(previous.home_goals, previous.guest_goals, outcome(game, team))
    start = game.opening_whistle
    end = start + timedelta(minutes=90)
    dtstamp = datetime.now()
    # todo: read location from game.sports_hall / game.location
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


def outcome(game, team):
    mapping = {
        TeamOutCome.WIN: 'Sieg',
        TeamOutCome.LOSS: 'Niederlage',
        TeamOutCome.TIE: 'Unentschieden',
    }
    outcome = game.outcome_for(team)
    return mapping.get(outcome)


def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()
