"""
Unit tests for Upstox and external infrastructure HTTP clients.
"""

from datetime import date
from unittest.mock import MagicMock, patch

from apps.stock_data_management.infrastructure.clients.company_financial_data_client import CompanyFinancialDataClient
from apps.stock_data_management.infrastructure.clients.stock_historical_data_client import StockHistoricalDataClient
from apps.stock_data_management.infrastructure.clients.stock_instruments_client import StockInstrumentsClient
from apps.stock_data_management.infrastructure.clients.upstox_client import UpstoxClient


class TestUpstoxClient:
    """Test suite for Upstox base client initialization and accessor methods."""

    @patch("apps.stock_data_management.infrastructure.clients.upstox_client.redis_client")
    @patch("apps.stock_data_management.infrastructure.clients.upstox_client.HttpClient")
    def test_upstox_client_methods(self, mock_http_cls, mock_redis):
        client = UpstoxClient()
        assert client.get_http_client() is not None


class TestStockHistoricalDataClient:
    """Test suite for StockHistoricalDataClient endpoint construction."""

    def test_get_historical_data_from_upstox(self, mock_upstox_client):
        mock_http = MagicMock()
        mock_http.get_json.return_value = {"data": {"candles": []}}
        mock_upstox_client.get_http_client.return_value = mock_http
        mock_upstox_client.get_valid_token.return_value = "token_abc"

        client = StockHistoricalDataClient(mock_upstox_client)
        data = client.get_historical_data_from_upstox(
            instrument_key="NSE_EQ|INE002A01018",
            unit="days",
            interval_option=1,
            to_date=date(2024, 1, 31),
            from_date=date(2024, 1, 1)
        )

        assert data == {"candles": []}
        mock_http.get_json.assert_called_once()
        called_url = mock_http.get_json.call_args[0][0]
        assert "NSE_EQ|INE002A01018" in called_url
        assert "2024-01-31/2024-01-01" in called_url


class TestStockInstrumentsClient:
    """Test suite for StockInstrumentsClient."""

    def test_get_instrument_profile_from_upstox(self, mock_upstox_client):
        mock_http = MagicMock()
        mock_http.get_json.return_value = {"data": {"company_name": "RELIANCE"}}
        mock_upstox_client.get_http_client.return_value = mock_http
        mock_upstox_client.get_valid_token.return_value = "token_abc"

        client = StockInstrumentsClient(mock_upstox_client)
        data = client.get_instrument_profile_from_upstox(isin="INE002A01018")

        assert data == {"company_name": "RELIANCE"}
        mock_http.get_json.assert_called_once()


class TestCompanyFinancialDataClient:
    """Test suite for CompanyFinancialDataClient statement endpoints."""

    def test_get_balance_sheet_from_upstox(self, mock_upstox_client):
        mock_http = MagicMock()
        mock_http.get_json.return_value = {"data": {"unit": "crores"}}
        mock_upstox_client.get_http_client.return_value = mock_http
        mock_upstox_client.get_valid_token.return_value = "token_abc"

        client = CompanyFinancialDataClient(mock_upstox_client)
        data = client.get_balance_sheet_from_upstox(isin="INE002A01018")

        assert data == {"unit": "crores"}
        mock_http.get_json.assert_called_once()

    def test_get_cash_flow_from_upstox(self, mock_upstox_client):
        mock_http = MagicMock()
        mock_http.get_json.return_value = {"data": {"unit": "crores"}}
        mock_upstox_client.get_http_client.return_value = mock_http
        mock_upstox_client.get_valid_token.return_value = "token_abc"

        client = CompanyFinancialDataClient(mock_upstox_client)
        data = client.get_cash_flow_from_upstox(isin="INE002A01018")

        assert data == {"unit": "crores"}
        mock_http.get_json.assert_called_once()

    def test_get_income_statement_from_upstox(self, mock_upstox_client):
        mock_http = MagicMock()
        mock_http.get_json.return_value = {"data": {"unit": "crores"}}
        mock_upstox_client.get_http_client.return_value = mock_http
        mock_upstox_client.get_valid_token.return_value = "token_abc"

        client = CompanyFinancialDataClient(mock_upstox_client)
        data = client.get_income_statement_from_upstox(isin="INE002A01018")

        assert data == {"unit": "crores"}
        mock_http.get_json.assert_called_once()
