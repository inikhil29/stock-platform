
from apps.nse.config.settings import settings
from core.clients.http_client import HttpClient


class NseClient():
    def __init__(self):
        self._http = HttpClient(settings.NSE_LIVE_URL)
        self._headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/"
        }
        self._http._session.headers.update(self._headers)
        self.init_cookies()

    def get_http_client(self):
        return self._http

    def init_cookies(self):
        self._http.get("/", timeout=10)
