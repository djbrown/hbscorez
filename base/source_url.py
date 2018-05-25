ROOT_SOURCE_URL = 'https://spo.handball4all.de/'


def associations_source_url():
    return ROOT_SOURCE_URL


def association_source_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID={}'.format(bhv_id)


def district_source_url(bhv_id, date=None):
    date_suffix = '&do={}'.format(date) if date else ''
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&orgID={}{}'.format(bhv_id, date_suffix)


def league_source_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?&orgGrpID=1&all=1&score={}'.format(bhv_id)


def team_source_url(bhv_id, team_bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&score={}&teamID={}'.format(bhv_id, team_bhv_id)


def sports_hall_source_url(bhv_id):
    return ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&gymID={}'.format(bhv_id)


def report_source_url(report_number):
    return ROOT_SOURCE_URL + 'misc/sboPublicReports.php?sGID={}'.format(report_number)
