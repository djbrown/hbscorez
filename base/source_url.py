def associations_url():
    return 'https://spo.handball4all.de/'


def association_url(bhv_id):
    return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}'.format(bhv_id)


def district_url(bhv_id):
    return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=1&orgID={}'.format(bhv_id)


def league_source_url(bhv_id):
    return 'https://spo.handball4all.de/Spielbetrieb/index.php?&orgGrpID=1&all=1&score={}'.format(bhv_id)


def team_source_url(league_bhv_id, team_bhv_id):
    return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=1&score={}&teamID={}'.format(
        league_bhv_id, team_bhv_id)


def sports_hall_source_url(bhv_id):
    return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=1&gymID={}'.format(bhv_id)


def report_url(report_number):
    return 'https://spo.handball4all.de/misc/sboPublicReports.php?sGID={}'.format(report_number)
