"""
Unit tests for UpstoxAccessTokenManager.
"""

from unittest.mock import MagicMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytest

from apps.stock_data_management.services.upstox_access_token_manager import UpstoxAccessTokenManager

ist_tz = ZoneInfo("Asia/Kolkata")


class TestUpstoxAccessTokenManager:
    """Test suite for Upstox OAuth token lifecycle and concurrency management."""

    def test_get_valid_token_cached(self):
        mock_store = MagicMock()
        mock_auth_client = MagicMock()

        future_expiry = datetime.now(ist_tz) + timedelta(hours=2)
        mock_store.get_token.return_value = {
            "access_token": "cached_valid_token",
            "expires_at": future_expiry.isoformat()
        }

        manager = UpstoxAccessTokenManager(mock_store, mock_auth_client)
        token = manager.get_valid_token()

        assert token == "cached_valid_token"
        mock_auth_client.refresh_token.assert_not_called()

    def test_is_token_valid_false_when_no_token(self):
        mock_store = MagicMock()
        mock_auth_client = MagicMock()
        manager = UpstoxAccessTokenManager(mock_store, mock_auth_client)

        assert manager._is_token_valid(None) is False
        assert manager._is_token_valid({}) is False

    def test_is_token_valid_false_when_expiring_within_60s(self):
        mock_store = MagicMock()
        mock_auth_client = MagicMock()
        manager = UpstoxAccessTokenManager(mock_store, mock_auth_client)

        near_expiry = datetime.now(ist_tz) + timedelta(seconds=30)
        token_data = {
            "access_token": "expiring_soon_token",
            "expires_at": near_expiry.isoformat()
        }

        assert manager._is_token_valid(token_data) is False

    def test_refresh_and_store_flow(self):
        mock_store = MagicMock()
        mock_auth_client = MagicMock()
        mock_auth_client.refresh_token.return_value = {
            "access_token": "newly_refreshed_token"
        }

        mock_store.get_token.return_value = None  # Cache miss

        manager = UpstoxAccessTokenManager(mock_store, mock_auth_client)
        token = manager.get_valid_token()

        assert token == "newly_refreshed_token"
        mock_auth_client.refresh_token.assert_called_once()
        mock_store.set_token.assert_called_once()


