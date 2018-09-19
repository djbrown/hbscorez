import locale
import re
from datetime import datetime, timedelta
from typing import Match, Optional, Tuple
from urllib.parse import parse_qs, urlsplit


def parse_link_query_item(link, query_key):
    href = link.get('href')
    query = urlsplit(href).query
    return parse_qs(query)[query_key][0]


def parse_association_bhv_id(link):
    return int(parse_link_query_item(link, 'orgGrpID'))


def parse_district_link_date(link):
    return parse_link_query_item(link, 'do')


def parse_league_bhv_id(link):
    return int(parse_link_query_item(link, 'score'))


def parse_district_season_start_year(district_season_heading):
    matches = re.match("Halle(?:nrunde)? (\d{4})/(\d{4})", district_season_heading)
    return int(matches.group(1)) if matches else None


def parse_league_name(tree):
    heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
    return heading.split(' - ')[0]


def parse_team_bhv_id(link):
    return int(parse_link_query_item(link, 'teamID'))


def parse_team_names(text: str) -> Tuple[str, str]:
    match: Optional[Match[str]] = re.match('(.+) - (.+)', text)
    if match:
        return match.group(1), match.group(2)
    raise ValueError('invalid team names: {}'.format(text))


def parse_game_rows(dom):
    return dom.xpath('//table[@class="gametable"]/tr[position() > 1]')


def parse_opening_whistle(text) -> Optional[datetime]:
    if not text.strip():
        return None
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    if len(text) == 12:
        return datetime.strptime(text, '%a, %d.%m.%y')
    if len(text) == 20:
        return datetime.strptime(text, '%a, %d.%m.%y, %H:%Mh')
    raise ValueError('invalid opening whistle: {}'.format(text))


def parse_sports_hall_bhv_id(link):
    return int(parse_link_query_item(link, 'gymID'))


def parse_coordinates(tree) -> Tuple[Optional[str], Optional[str]]:
    scripts = tree.xpath('//script')
    map_script = scripts[4].text
    match = re.search("^   new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)\),$", map_script, re.MULTILINE)
    if match:
        return match.group(1), match.group(2)
    raise ValueError('coordinates not found: {}'.format(map_script))


def parse_goals(game_row) -> Tuple[int, int]:
    home_goals = game_row[7].text
    guest_goals = game_row[9].text
    if home_goals and guest_goals:
        return int(home_goals), int(guest_goals)

    if len(game_row[10]) == 1:
        title = game_row[10][0].get("title", "")
        match = re.match("SpA\((\d+):(\d+)\)", title)
        if match:
            return int(match.group(1)), int(match.group(2))

    raise ValueError('no goals found: {}'.format(game_row))


def parse_report_number(cell):
    if len(cell) >= 1 and cell[0].text == 'PI':
        return int(parse_link_query_item(cell[0], 'sGID'))

    return None


def parse_forfeiting_team(cell, home_team, guest_team):
    if cell.text == " (2:0)":
        return guest_team
    if cell.text == " (0:2)":
        return home_team
    raise ValueError('invalid forfeit: {}'.format(cell.text))


def parse_game_time(text: str) -> Optional[timedelta]:
    if not text:
        return None

    minutes, seconds = text.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))


def parse_penalty_data(text: str) -> Tuple[int, int]:
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0
