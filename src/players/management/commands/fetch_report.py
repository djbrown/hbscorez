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
    for retry_duration in RETRY_DURATIONS:
        try:
            return requests.get(game.report_source_url(), stream=True)
        except requests.exceptions.ConnectionError as ex:
            LOGGER.warning('Could not fetch report %s', game)
            if retry_duration <= MAX_RETRY_DURATION:
                LOGGER.debug('Now wating for %s', retry_duration)
                time.sleep(retry_duration.total_seconds())
    raise ex
