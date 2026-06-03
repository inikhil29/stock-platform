from apps.upstox.config.settings import settings
from apps.upstox.services.upstox_access_token_manager import UpstoxAccessTokenManager
from apps.upstox.infrastructure.clients.upstox_auth_client import UpstoxAuthClient
from apps.upstox.infrastructure.store.upstox_token_store import UpstoxAccessTokenStore
from core.clients.http_client import HttpClient
from core.cache.redis_client import redis_client


http = HttpClient(settings.UPSTOX_LIVE_URL) 
upstox_auth_client = UpstoxAuthClient(settings.UPSTOX_API_KEY, settings.UPSTOX_API_SECRET, settings.UPSTOX_REDIRECT_URI, http)
upstox_access_token_store = UpstoxAccessTokenStore(redis_client)

token_manager = UpstoxAccessTokenManager(upstox_access_token_store, upstox_auth_client)
print(token_manager.get_valid_token())