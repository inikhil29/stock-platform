"""
Unit tests for StockInstrumentsService.
"""

from unittest.mock import MagicMock
import pytest

from apps.stock_data_management.services.stock_instruments_service import StockInstrumentsService


class TestStockInstrumentsService:
    """Test suite for StockInstrumentsService transformation and sync routines."""

    def test_transform_record(self, mock_unit_of_work):
        client = MagicMock()
        service = StockInstrumentsService(mock_unit_of_work, client)

        valid_columns = {"instrument_key": None, "tradingsymbol": None, "tick_size": None, "last_price": None}
        raw_record = {
            "instrument_key": "NSE_EQ|INE002A01018",
            "tradingsymbol": "RELIANCE",
            "tick_size": 0.05,
            "last_price": 2900.0,
            "extra_field_from_api": "discard_me"
        }

        transformed = service._transform_record(raw_record, valid_columns)
        assert "extra_field_from_api" not in transformed
        assert transformed["instrument_key"] == "NSE_EQ|INE002A01018"
        assert transformed["tradingsymbol"] == "RELIANCE"

    def test_process_batch(self, mock_unit_of_work):
        client = MagicMock()
        service = StockInstrumentsService(mock_unit_of_work, client)

        batch = [{"instrument_key": "NSE_EQ|INE002A01018", "tradingsymbol": "RELIANCE"}]
        mock_unit_of_work.stock_instruments_repository.bulk_upsert.return_value = 1

        service.process_batch(batch)
        mock_unit_of_work.stock_instruments_repository.bulk_upsert.assert_called_once_with(
            batch
        )

    def test_get_instrument_details(self, mock_unit_of_work):
        client = MagicMock()
        service = StockInstrumentsService(mock_unit_of_work, client)

        mock_unit_of_work.stock_instruments_repository.find_one.return_value = {
            "instrument_key": "NSE_EQ|INE002A01018",
            "tradingsymbol": "RELIANCE"
        }

        details = service.get_instrument_details("NSE_EQ|INE002A01018")
        assert details["tradingsymbol"] == "RELIANCE"

    def test_fetch_instrument_keys_from_isin(self, mock_unit_of_work):
        client = MagicMock()
        service = StockInstrumentsService(mock_unit_of_work, client)

        mock_unit_of_work.stock_instruments_repository.fetch_instrument_keys_from_isin.return_value = [
            "NSE_EQ|INE002A01018", "BSE_EQ|INE002A01018"
        ]

        keys = service.fetch_instrument_keys_from_isin("INE002A01018")
        assert len(keys) == 2
        assert "NSE_EQ|INE002A01018" in keys

