import locale
import re
import typing
from datetime import datetime, timedelta
from urllib.parse import urlsplit, parse_qs


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
    matches = re.search("( \d{4})/(\d{4})", district_season_heading.text)
    return int(matches.group(1))


def parse_league_name(tree):
    heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
    return heading.split(' - ')[0]


def parse_team_bhv_id(link):
    return int(parse_link_query_item(link, 'teamID'))


def parse_team_names(text: str) -> (int, int):
    match = re.match("(.+) - (.+)", text)
    return match.group(1), match.group(2)


def parse_game_rows(dom):
    return dom.xpath('//table[@class="gametable"]/tr[position() > 1]')


def parse_opening_whistle(text) -> typing.Optional[datetime]:
    if not text.strip():
        return None
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    if len(text) == 12:
        return datetime.strptime(text, '%a, %d.%m.%y')
    elif len(text) == 20:
        return datetime.strptime(text, '%a, %d.%m.%y, %H:%Mh')
    else:
        raise Exception()


def parse_sports_hall_bhv_id(link):
    return int(parse_link_query_item(link, 'gymID'))


def parse_coordinates(tree):
    scripts = tree.xpath('//script')
    if len(scripts) >= 5:
        map_script = scripts[4].text
        return re.search("^   new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)\),$",
                         map_script, re.MULTILINE).groups()
    else:
        return None, None


def parse_goals(game_row) -> (int, int):
    home_goals = int(game_row[7].text) if game_row[7].text else None
    guest_goals = int(game_row[9].text) if game_row[9].text else None

    if home_goals is None and guest_goals is None and len(game_row[10]) == 1:
        title = game_row[10][0].get("title", "")
        match = re.match("SpA\((\d+):(\d+)\)", title)
        if match:
            home_goals = match.group(1)
            guest_goals = match.group(2)

    return home_goals, guest_goals


def parse_report_number(cell):
    if len(cell) >= 1 and cell[0].text == 'PI':
        return int(parse_link_query_item(cell[0], 'sGID'))
    else:
        return None


def parse_forfeiting_team(cell, home_team, guest_team):
    if cell.text == " (2:0)":
        return guest_team
    if cell.text == " (0:2)":
        return home_team


def parse_game_time(text: str) -> typing.Optional[timedelta]:
    if not text:
        return None

    minutes, seconds = text.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))


def parse_penalty_data(text: str) -> (int, int):
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return match.group(1), match.group(2)
    return 0, 0
