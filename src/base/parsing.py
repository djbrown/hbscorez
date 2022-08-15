import locale
import re
from datetime import datetime, timedelta
from typing import Match, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from lxml import html


def html_dom(html_text: str):
    return html.fromstring(html_text)


def parse_association_urls(dom, root_url):
    items = dom.xpath('//div[@id="main-content"]//table[@summary]/tbody/tr/td[1]/a/@href')
    return [item if item.startswith('http') else root_url + item for item in items]


def parse_association_bhv_id_from_dom(dom):
    [bhv_id] = dom.xpath('//div[@id="app"]/@data-og-id')
    return int(bhv_id)


def parse_link_query_item(link, query_key):
    href = link.get('href')
    query = urlsplit(href).query
    return parse_qs(query)[query_key][0]


def parse_association_bhv_id(link):
    return int(parse_link_query_item(link, 'orgGrpID'))


def parse_association_name(dom):
    heading = dom.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
    return heading.rsplit(' - ', 1)[0]


def parse_district_link_date(link):
    return parse_link_query_item(link, 'do')


def parse_league_bhv_id(link):
    return int(parse_link_query_item(link, 'score'))


def parse_district_season_start_year(district_season_heading):
    matches = re.match(r"Halle(?:nrunde)? (\d{4})/(\d{4})", district_season_heading)
    return int(matches.group(1)) if matches else None


def parse_league_name(dom):
    heading = dom.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
    return heading.rsplit(' - ', 1)[0]


def parse_team_links(dom):
    return dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a') or \
        dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[2]/a')


def parse_retirements(dom):
    retirements = []
    paragraphs = dom.xpath('//table[@class="scoretable"]/following::div[following::table[@class="gametable"]]')
    for paragraph in paragraphs:
        text = paragraph.text_content()
        matches = re.match(r"(?:Der|Die) (.*) hat.* ([0123]\d\.[012]\d\.\d{2,4}).* zurückgezogen.*", text)
        if matches:
            team_name = matches.group(1)

            def date_from_text(text):
                for date_format in ['%d.%m.%y', '%d.%m.%Y']:
                    try:
                        return datetime.strptime(text, date_format).date()
                    except ValueError:
                        pass
                raise ValueError('no date format is valid')

            retirement_date = date_from_text(matches.group(2))
            retirements.append((team_name, retirement_date))
    return retirements


def parse_team_bhv_id(link):
    return int(parse_link_query_item(link, 'teamID'))


def parse_team_names(text: str) -> Tuple[str, str]:
    match: Optional[Match[str]] = re.match(r"(.+) - (.+)", text)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f'invalid team names: {text}')


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
    raise ValueError(f'invalid opening whistle: {text}')


def parse_sports_hall_bhv_id(link):
    return int(parse_link_query_item(link, 'gymID'))


def parse_coordinates(dom) -> Tuple[Optional[str], Optional[str]]:
    map_scripts = dom.xpath('//script[contains(text(),"new mxn.LatLonPoint")]')
    if not map_scripts:
        return (None, None)
    match = re.search(r"new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)", map_scripts[0].text)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f'coordinates not found: {map_scripts}')


def parse_goals(game_row) -> Tuple[Optional[int], Optional[int]]:
    home_goals = game_row[7].text
    guest_goals = game_row[9].text
    if home_goals and guest_goals:
        home_goals = home_goals.strip()
        guest_goals = guest_goals.strip()
        if home_goals and guest_goals:
            return int(home_goals), int(guest_goals)

    if len(game_row[10]) == 1:
        title = game_row[10][0].get("title", "")
        match = re.match(r"SpA\((\d+):(\d+)\)", title)
        if match:
            return int(match.group(1)), int(match.group(2))

    return (None, None)


def parse_report_number(cell):
    if len(cell) >= 1 and cell[0].text == 'PI':
        return int(parse_link_query_item(cell[0], 'sGID'))

    return None


def parse_forfeiting_team(cell, home_team, guest_team):
    text = str(html.tostring(cell))
    if "2:0" in text:
        return guest_team
    if "0:2" in text:
        return home_team
    return None


def parse_game_time(text: str) -> Optional[timedelta]:
    if not text:
        return None

    minutes, seconds = text.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))


def parse_penalty_data(text: str) -> Tuple[int, int]:
    match = re.match(r"(\d+)/(\d+)", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0
