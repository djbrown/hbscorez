import time

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util import Retry

_http = requests.Session()
_http.mount("https://", HTTPAdapter(max_retries=Retry()))


def get_text(url) -> str:
    response = _http.get(url, timeout=5)
    response.encoding = "utf-8"
    return response.text


def get_throttled(url, wait=5) -> str:
    time.sleep(wait)
    return get_text(url)


class EmptyResponseError(RequestException):
    """The response payload was empty."""


def get_file(url: str) -> bytes:
    response = _http.get(url, stream=True, timeout=5)
    if int(response.headers.get("Content-Length", -1)) == 0:
        raise EmptyResponseError()
    return response.content
