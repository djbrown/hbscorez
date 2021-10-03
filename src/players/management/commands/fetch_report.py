import logging
import time
from datetime import timedelta
from typing import List

import requests

from games.models import Game

MAX_RETRY_DURATION: timedelta = timedelta(hours=1)
RETRY_DURATIONS: List[timedelta] = [
    timedelta(seconds=10),
    timedelta(seconds=30),
    timedelta(minutes=1),
    timedelta(minutes=5),
    timedelta(minutes=10),
    timedelta(minutes=30),
    MAX_RETRY_DURATION,
]

LOGGER = logging.getLogger('hbscorez')


def fetch_report(game: Game):
    return retry_downloads(game, RETRY_DURATIONS)


def retry_downloads(game: Game, retry_durations: List[timedelta]):
    try:
        url = game.report_source_url()
        return requests.get(url, stream=True, timeout=5)
    except requests.exceptions.ConnectionError as exc:
        if len(retry_durations) == 0:
            raise exc
        retry_duration = retry_durations[0]
        LOGGER.warning('Could not fetch report %s', game)
        LOGGER.debug('Now wating for %s', retry_duration)
        time.sleep(retry_duration.total_seconds())
        return retry_downloads(game, retry_durations[1:])
