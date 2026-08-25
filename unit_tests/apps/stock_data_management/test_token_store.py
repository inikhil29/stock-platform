"""
Unit tests for UpstoxAccessTokenStore.
"""

from unittest.mock import MagicMock
from apps.stock_data_management.infrastructure.store.upstox_token_store import UpstoxAccessTokenStore


class TestUpstoxAccessTokenStore:
    """Test suite for UpstoxAccessTokenStore caching methods."""

    def test_get_token(self, mock_redis_client):
        mock_redis_client.get.return_value = "token_xyz"
        store = UpstoxAccessTokenStore(mock_redis_client)

        token = store.get_token()
        assert token == "token_xyz"
        mock_redis_client.get.assert_called_once_with(store.redis_access_token_key)

    def test_set_token(self, mock_redis_client):
        store = UpstoxAccessTokenStore(mock_redis_client)
        store.set_token("new_token", ttl=3600)

        mock_redis_client.set.assert_called_once_with(
            store.redis_access_token_key,
            "new_token",
            3600
        )

    def test_acquire_lock(self, mock_redis_client):
        mock_redis_client.set_if_not_exists.return_value = True
        store = UpstoxAccessTokenStore(mock_redis_client)

        locked = store.acquire_lock()
        assert locked is True
        mock_redis_client.set_if_not_exists.assert_called_once()

