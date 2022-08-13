import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util import Retry

http = requests.Session()
http.mount("https://",  HTTPAdapter(max_retries=Retry()))

class EmptyResponseError(RequestException):
    """The response payload was empty."""


def get_file(url: str) -> bytes:
    response = http.get(url, stream=True, timeout=5)
    if int(response.headers.get('Content-Length', -1)) == 0:
        raise EmptyResponseError()
    return response.content
