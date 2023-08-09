import locale
import re
from datetime import datetime, timedelta
from typing import cast
from urllib.parse import parse_qs, urlsplit

import json

from lxml import html
from lxml.etree import _Element

from games.models import SportsHall
from teams.models import Team


def html_dom(html_text: str) -> _Element:
    return html.fromstring(html_text)


def parse_link_query_item(link: _Element, query_key: str) -> str:
    href = link.get('href')
    query = cast(str, urlsplit(href).query)
    return parse_qs(query)[query_key][0]


def parse_association_urls(dom: _Element) -> list[str]:
    return cast(list[str], dom.xpath('//ul[@id="main-navi"]/li[contains(@class, "active")]//li/a/@href'))


def parse_association_abbreviation(association_url: str) -> str:
    return association_url.rsplit('/', 1)[1]


def parse_association_name(dom: _Element) -> str:
    return cast(list[str], dom.xpath('//h2/a/text()'))[0]


def parse_association_bhv_id(dom: _Element) -> int:
    [bhv_id] = cast(list[str], dom.xpath('//div[@id="app"]/@data-og-id'))
    return int(bhv_id)


def parse_district_items(response: str) -> dict | None:
    try:
        return json.loads(response)[0]['menu']['org']['list']
    except ValueError:
        return None


def parse_district_link_date(link: _Element) -> str:
    return parse_link_query_item(link, 'do')


def parse_league_links(dom: _Element) -> list[_Element]:
    return cast(list[_Element], dom.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a'))


def parse_league_bhv_id(link: _Element) -> int:
    return int(parse_link_query_item(link, 'score'))


def parse_district_season_start_year(district_season_heading: str) -> int | None:
    matches = re.match(r"Halle(?:nrunde)? (\d{4})/(\d{4})", district_season_heading)
    return int(matches.group(1)) if matches else None


def parse_league_name(dom: _Element) -> str:
    heading = cast(list[str], dom.xpath('//*[@id="results"]/div/h1/text()[2]'))[0]
    return heading.rsplit(' - ', 1)[0]


def parse_team_links(dom: _Element) -> list[_Element]:
    return cast(list[_Element], dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a')) or \
        cast(list[_Element], dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[2]/a'))


def parse_retirements(dom: _Element) -> list[tuple[str, datetime]]:
    retirements = []
    paragraphs = cast(list[html.HtmlMixin], dom.xpath(
        '//table[@class="scoretable"]/following::div[following::table[@class="gametable"]]'))
    for paragraph in paragraphs:
        text: str = cast(str, paragraph.text_content())
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


def parse_team_bhv_id(link: _Element) -> int:
    return int(parse_link_query_item(link, 'teamID'))


def parse_team_names(text: str) -> tuple[str, str]:
    match: re.Match[str] | None = re.match(r"(.+) - (.+)", text)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f'invalid team names: {text}')


def parse_game_rows(dom: _Element) -> list[_Element]:
    return cast(list[_Element], dom.xpath('//table[@class="gametable"]/tr[position() > 1]'))


def parse_team_short_names(game_rows: list[_Element]) -> list[str | None]:
    return [c.text for game_row in game_rows for c in cast(list[_Element], game_row.xpath('td'))[4:7:2]]


def parse_opening_whistle(text: str) -> datetime | None:
    if not text.strip():
        return None
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    if len(text) == 12:
        return datetime.strptime(text, '%a, %d.%m.%y')
    if len(text) == 20:
        return datetime.strptime(text, '%a, %d.%m.%y, %H:%Mh')
    raise ValueError(f'invalid opening whistle: {text}')


def parse_sports_hall(dom: _Element) -> SportsHall:
    table = cast(list[_Element], dom.xpath('//table[@class="gym"]'))[0]
    name = cast(str, table[0][1][0].text)
    city = cast(str, table[1][1].text)
    street = table[2][1].text
    address = street + ", " + city if street else city
    phone_number = table[3][1].text

    latitude, longitude = parse_coordinates(dom)

    return SportsHall(name=name, address=address,
                      phone_number=phone_number, latitude=latitude,
                      longitude=longitude)


def parse_sports_hall_bhv_id(link: _Element) -> int:
    return int(parse_link_query_item(link, 'gymID'))


def parse_coordinates(dom: _Element) -> tuple[str | None, str | None]:
    map_scripts = cast(list[_Element], dom.xpath('//script[contains(text(),"new mxn.LatLonPoint")]'))
    if not map_scripts or not map_scripts[0].text:
        return (None, None)
    match = re.search(r"new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)", map_scripts[0].text)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f'coordinates not found: {map_scripts}')


def parse_goals(game_row: _Element) -> tuple[int | None, int | None]:
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


def parse_report_number(cell: _Element) -> int | None:
    if len(cell) >= 1 and cell[0].text == 'PI':
        return int(parse_link_query_item(cell[0], 'sGID'))

    return None


def parse_forfeiting_team(cell: _Element, home_team: Team, guest_team: Team) -> Team | None:
    text = str(html.tostring(cell))
    if "2:0" in text:
        return guest_team
    if "0:2" in text:
        return home_team
    return None


def parse_game_time(text: str) -> timedelta | None:
    if not text:
        return None

    minutes, seconds = text.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))


def parse_penalty_data(text: str) -> tuple[int, int]:
    match = re.match(r"(\d+)/(\d+)", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0
