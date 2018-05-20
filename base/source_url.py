import datetime

ROOT_SOURCE_URL = 'https://spo.handball4all.de/'


def associations_url():
    return ROOT_SOURCE_URL


def association_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID={}'.format(bhv_id)


def district_url(bhv_id, date=datetime.date.today()):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&orgID={}&do={}'.format(bhv_id, date)


def league_season_source_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?&orgGrpID=1&all=1&score={}'.format(bhv_id)


def team_source_url(league_season_bhv_id, team_bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&score={}&teamID={}'.format(
        league_season_bhv_id, team_bhv_id)


def sports_hall_source_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&gymID={}'.format(bhv_id)


def report_url(report_number):
    return ROOT_SOURCE_URL + 'misc/sboPublicReports.php?sGID={}'.format(report_number)
