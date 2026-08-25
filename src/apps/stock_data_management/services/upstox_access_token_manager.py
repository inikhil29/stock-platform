"""
Upstox Access Token Manager Module.

Responsible for managing the lifecycle, thread-safe renewal, validation,
and caching of Upstox API OAuth access tokens.
"""

from datetime import datetime, timedelta
import threading
from zoneinfo import ZoneInfo

from apps.stock_data_management.infrastructure.clients.upstox_auth_client import UpstoxAuthClient
from apps.stock_data_management.infrastructure.store.upstox_token_store import UpstoxAccessTokenStore

timezone = ZoneInfo("Asia/Kolkata")


class UpstoxAccessTokenManager:
    """
    Manages access token retrieval, validity checking, and thread-safe refreshing
    for authenticating requests with Upstox API v2/v3.

    Attributes:
        store (UpstoxAccessTokenStore): Cache store (Redis) for persisting token metadata.
        auth_client (UpstoxAuthClient): Client handling interactive or OAuth authorization.
    """

    def __init__(self, store: UpstoxAccessTokenStore, auth_client: UpstoxAuthClient):
        """
        Initialize the UpstoxAccessTokenManager with token storage and auth clients.

        Parameters:
            store (UpstoxAccessTokenStore): Storage layer for caching access token and expiration.
            auth_client (UpstoxAuthClient): Auth client for generating fresh access tokens via OAuth.
        """
        self.store = store
        self.auth_client = auth_client
        self._lock = threading.Lock()

    def _is_token_valid(self, token_data: dict | None) -> bool:
        """
        Check whether the cached token data exists and is not expired (with safety margin).

        Parameters:
            token_data (dict | None): Dictionary containing token details:
                - 'access_token' (str): The OAuth bearer token string.
                - 'expires_at' (str): ISO formatted timestamp of token expiration.

        Returns:
            bool: True if the token is present and valid for at least 60 more seconds, False otherwise.
        """
        if not token_data or "expires_at" not in token_data or "access_token" not in token_data:
            return False
        try:
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            now = datetime.now(timezone)
            # 60-second safety margin to avoid edge-of-expiry request failures
            return expires_at > (now + timedelta(seconds=60))
        except Exception:
            return False

    def get_valid_token(self) -> str:
        """
        Retrieve a valid access token.

        First checks the cache store. If the token is absent or expired,
        acquires a lock to refresh the token from Upstox and updates the cache.

        Returns:
            str: Valid Upstox API OAuth access token.
        """
        token_data = self.store.get_token()
        if self._is_token_valid(token_data):
            return token_data["access_token"]

        return self._refresh_with_lock()

    def _refresh_with_lock(self) -> str:
        """
        Acquire thread lock and refresh access token with double-checked caching.

        Ensures multiple concurrent threads do not initiate redundant authorization flows.

        Returns:
            str: Fresh or existing valid Upstox OAuth access token.
        """
        with self._lock:
            # Re-check under lock in case another thread already completed token refresh
            token_data = self.store.get_token()
            if self._is_token_valid(token_data):
                return token_data["access_token"]
            return self._refresh_and_store()

    def _refresh_and_store(self) -> str:
        """
        Obtain a new access token from Upstox via OAuth and save it to the cache store with TTL.

        Upstox access tokens expire daily at 03:30 AM IST. Calculates the TTL until the
        next 03:30 AM IST cycle and stores the token in Redis.

        Returns:
            str: Newly generated Upstox access token.
        """
        new_token = self.auth_client.refresh_token()
        now = datetime.now(timezone)
        today_330 = now.replace(hour=3, minute=30, second=0, microsecond=0)

        # Calculate expiration time: Upstox tokens expire daily at 03:30 AM IST
        if now >= today_330:
            expires_at = today_330 + timedelta(days=1)
        else:
            expires_at = today_330

        ttl_seconds = max(int((expires_at - now).total_seconds()), 60)
        self.store.set_token({
            "access_token": new_token["access_token"],
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat()
        }, ttl=ttl_seconds)

        return new_token["access_token"]
