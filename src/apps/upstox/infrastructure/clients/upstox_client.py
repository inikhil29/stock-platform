
from apps.upstox.config.settings import settings
from apps.upstox.services.upstox_access_token_manager import UpstoxAccessTokenManager
from apps.upstox.infrastructure.clients.upstox_auth_client import UpstoxAuthClient
from apps.upstox.infrastructure.store.upstox_token_store import UpstoxAccessTokenStore
from core.clients.http_client import HttpClient
from core.cache.redis_client import redis_client


class UpstoxClient():
    def __init__(self):
        self._http = HttpClient(settings.UPSTOX_LIVE_URL) 
        self._upstox_auth_client = UpstoxAuthClient(settings.UPSTOX_API_KEY, settings.UPSTOX_API_SECRET, settings.UPSTOX_REDIRECT_URI, self._http)
        self._upstox_access_token_store = UpstoxAccessTokenStore(redis_client)
        self._token_manager = UpstoxAccessTokenManager(self._upstox_access_token_store, self._upstox_auth_client)
        
        
    def get_valid_token(self):
        return self._token_manager.get_valid_token()
    
    def get_http_client(self):
        return self._http