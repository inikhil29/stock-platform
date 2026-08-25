"""
Unit tests for StockHistoricalDataService.
"""

from datetime import date, datetime
from unittest.mock import MagicMock
import pytest

from apps.stock_data_management.services.stock_historical_data_service import StockHistoricalDataService
from core.enum.candle_interval_enum import CandleInterval


class TestStockHistoricalDataService:
    """Test suite for StockHistoricalDataService date partitioning, S3 streaming, and ingestion."""

    def test_get_max_date_limit_for_interval(self, mock_unit_of_work, mock_aws_client):
        client = MagicMock()
        service = StockHistoricalDataService(mock_unit_of_work, client, mock_aws_client)

        # Minutes/hours start at 2022-01-01
        assert service._get_max_date_limit_for_interval(CandleInterval.M1) == date(2022, 1, 1)
        assert service._get_max_date_limit_for_interval(CandleInterval.H1) == date(2022, 1, 1)

        # Daily/weekly/monthly start at 2000-01-01
        assert service._get_max_date_limit_for_interval(CandleInterval.D1) == date(2000, 1, 1)

    def test_generate_first_day_last_day_list_monthly(self, mock_unit_of_work, mock_aws_client):
        client = MagicMock()
        service = StockHistoricalDataService(mock_unit_of_work, client, mock_aws_client)

        ranges = service._generate_first_day_last_day_list(
            from_date=date(2024, 1, 15),
            to_date=date(2024, 3, 10),
            by='m'
        )

        assert len(ranges) >= 2
        # First chunk January 2024 (1 to 31)
        assert ranges[0][0] == date(2024, 1, 1)
        assert ranges[0][1] == date(2024, 1, 31)
        # Second chunk February 2024 (Leap year -> 29 days)
        assert ranges[1][0] == date(2024, 2, 1)
        assert ranges[1][1] == date(2024, 2, 29)

    def test_fetch_historical_data(self, mock_unit_of_work, mock_aws_client):
        client = MagicMock()
        client.get_historical_data_from_upstox.return_value = {"candles": []}
        service = StockHistoricalDataService(mock_unit_of_work, client, mock_aws_client)

        result = service._fetch_historical_data(
            instrument_key="NSE_EQ|INE002A01018",
            unit="minutes",
            interval_option=1,
            from_date="2024-01-01",
            to_date="2024-01-31"
        )
        assert result == {"candles": []}
        client.get_historical_data_from_upstox.assert_called_once()

