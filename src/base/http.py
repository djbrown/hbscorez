import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

retry_strategy = Retry(
    read=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=Retry())
http = requests.Session()
http.mount("https://", adapter)
