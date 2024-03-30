from datetime import timedelta
from enum import Enum, auto

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from icalendar import Calendar, Event, vText
from returns.result import Result

from base.logic import add_ranking_place
from games.models import Game, TeamOutcome
from players.models import Player
from teams.models import Team


def detail(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    return render(request, "teams/detail.j2", {"team": team})


def games(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team)).order_by("opening_whistle")
    return render(request, "teams/games.j2", {"team": team, "games": team_games})


def players(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_players = Player.objects.filter(team=team).annotate(games=Count("score")).order_by("name")
    return render(request, "teams/players.j2", {"team": team, "players": team_players})


def scorers(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_players = (
        Player.objects.filter(team=team)
        .annotate(games=Count("score"))
        .annotate(total_goals=Coalesce(Sum("score__goals"), 0))
        .filter(total_goals__gt=0)
        .annotate(total_penalty_goals=Sum("score__penalty_goals"))
        .annotate(total_field_goals=F("total_goals") - F("total_penalty_goals"))
        .order_by("-total_goals")
    )
    add_ranking_place(team_players, "total_goals")
    return render(request, "teams/scorers.j2", {"team": team, "players": team_players})


def offenders(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_offenders = (
        Player.objects.filter(team=team)
        .annotate(games=Count("score"))
        .annotate(warnings=Count("score__warning_time"))
        .annotate(
            suspensions=Count("score__first_suspension_time")
            + Count("score__second_suspension_time")
            + Count("score__third_suspension_time")
        )
        .annotate(disqualifications=Count("score__disqualification_time"))
        .annotate(offender_points=F("warnings") + 2 * F("suspensions") + 3 * F("disqualifications"))
        .filter(offender_points__gt=0)
        .order_by("-offender_points")
    )
    add_ranking_place(team_offenders, "offender_points")
    return render(request, "teams/offenders.j2", {"team": team, "offenders": team_offenders})


def calendar(_, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    team_games = Game.objects.filter(Q(home_team=team) | Q(guest_team=team))

    cal = Calendar()
    cal.add("PRODID", "-//HbScorez//Mannschaftskalender 1.0//DE")
    cal.add("VERSION", "2.0")
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("METHOD", "PUBLISH")
    cal.add("X-WR-CALNAME", f"Spielplan {team.league.abbreviation} {team.short_name}")
    cal.add("X-WR-TIMEZONE", "Europe/Berlin")
    cal.add(
        "X-WR-CALDESC",
        f'Spielplan der Mannschaft "{team.name}"'
        + f" in der Saison {team.league.season.start_year}/{team.league.season.start_year + 1}"
        + f' in der Liga "{team.league.name}" des Bereichs "{team.league.district.name}"',
    )

    for game in team_games:
        result = _create_event(team, game)
        result.bind(cal.add_component)

    return HttpResponse(cal.to_ical(), "text/calendar")


class ErrCode(Enum):
    MISSING_OPENING_WHISTLE = auto()


def _create_event(team: Team, game: Game) -> Result[Event, ErrCode]:
    if not game.opening_whistle:
        return Result.from_failure(ErrCode.MISSING_OPENING_WHISTLE)

    venue = "Heimspiel" if game.home_team == team else "Auswärtsspiel"
    summary = f"{venue} - {game.opponent_of(team).short_name}"

    leg_title = game.leg_title()
    description = f"{leg_title} gegen {game.opponent_of(team).name}"
    if game.sports_hall:
        description += "\nSporthalle: " + str(game.sports_hall.name)

    dated_games = game.other_games().filter(opening_whistle__isnull=False)
    for other in sorted(dated_games, key=lambda g: g.opening_whistle):
        if other.home_goals is not None:
            description += f"\n{other.leg_title()}: {other.home_goals}:{other.guest_goals} ({_outcome(other, team)})"

    start = game.opening_whistle
    end = start + timedelta(minutes=90)
    dtstamp = timezone.now()
    location = game.sports_hall.address if game.sports_hall else None
    uid = f"game/{game.number}@hbscorez.de"

    event = Event()
    event.add("summary", summary)
    event.add("description", description)
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("dtstamp", dtstamp)
    if location:
        event["location"] = vText(location)
    event["uid"] = uid

    return Result.from_value(event)


def _outcome(game, team):
    mapping = {
        TeamOutcome.WIN: "Sieg",
        TeamOutcome.LOSS: "Niederlage",
        TeamOutcome.TIE: "Unentschieden",
    }
    outcome = game.outcome_for(team)
    return mapping.get(outcome)
