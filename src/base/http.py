import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

http = requests.Session()
http.mount("https://",  HTTPAdapter(max_retries=Retry()))


