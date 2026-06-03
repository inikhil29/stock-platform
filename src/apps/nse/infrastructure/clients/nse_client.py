
from apps.nse.config.settings import settings
from core.clients.http_client import HttpClient


class NseClient():
    def __init__(self):
        self._http = HttpClient(settings.NSE_LIVE_URL)         
    
    def get_http_client(self):
        return self._http