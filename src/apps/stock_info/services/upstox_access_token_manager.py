from datetime import datetime, timedelta
import time
import threading
from zoneinfo import ZoneInfo

from apps.stock_info.infrastructure.clients.upstox_auth_client import UpstoxAuthClient
from apps.stock_info.infrastructure.store.upstox_token_store import UpstoxAccessTokenStore
timezone = ZoneInfo("Asia/Kolkata")


class UpstoxAccessTokenManager:
    def __init__(self, store: UpstoxAccessTokenStore, auth_client: UpstoxAuthClient):
        self.store = store
        self.auth_client = auth_client
        self._lock = threading.Lock()

    def get_valid_token(self):
        token_data = self.store.get_token()
        if token_data:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            now = datetime.now(timezone)
            if expires_at and expires_at > now:
                return token_data["access_token"]

        return self._refresh_and_store()

    def _refresh_with_lock(self):
        with self._lock:
            return self._refresh_and_store()

    def _refresh_and_store(self):

        new_token = self.auth_client.refresh_token()
        now = datetime.now(timezone)
        today_330 = now.replace(hour=3, minute=30, second=0, microsecond=0)

        if now >= today_330:
            expires_at = today_330 + timedelta(days=1)
        else:
            expires_at = today_330

        ttl_seconds = int((expires_at - now).total_seconds())
        self.store.set_token({
            "access_token": new_token["access_token"],
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat()
        }, ttl=ttl_seconds)

        return new_token["access_token"]
