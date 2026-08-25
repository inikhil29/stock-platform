"""
Unit tests for CompanyProfileService.
"""

from unittest.mock import MagicMock
import pytest

from apps.stock_data_management.services.company_profile_services import CompanyProfileService


class TestCompanyProfileService:
    """Test suite for CompanyProfileService dual-persistence and batch syncing."""

    def test_build_instrument_profile_payload(self, mock_unit_of_work):
        stock_instruments_service = MagicMock()
        mongo_repo = MagicMock()
        client = MagicMock()

        service = CompanyProfileService(
            unit_of_work=mock_unit_of_work,
            stock_instruments_service=stock_instruments_service,
            stock_instruments_profile_repository=mongo_repo,
            stock_instrument_client=client
        )

        raw_data = {
            "company_profile": "Sample description",
            "sector": "Technology",
            "sector_market_cap_inr": {"value": 100.0, "unit": "Cr", "formatted": "100 Cr"},
            "sector_market_cap_usd": {"value": 12.0, "unit": "M", "formatted": "$12M"}
        }

        payload = service._build_instrument_profile_payload("INE002A01018", raw_data)
        assert payload["isin"] == "INE002A01018"
        assert payload["company_profile"] == "Sample description"
        assert payload["sector"] == "Technology"

    def test_update_instrument_profile_persists_to_both_stores(self, mock_unit_of_work):
        stock_instruments_service = MagicMock()
        mongo_repo = MagicMock()
        client = MagicMock()

        client.get_instrument_profile_from_upstox.return_value = {
            "company_name": "RELIANCE INDUSTRIES LTD",
            "sector": "Energy - Oil & Gas",
            "company_profile": "Reliance is a diversified conglomerate.",
            "sector_market_cap_inr": None,
            "sector_market_cap_usd": None
        }

        service = CompanyProfileService(
            unit_of_work=mock_unit_of_work,
            stock_instruments_service=stock_instruments_service,
            stock_instruments_profile_repository=mongo_repo,
            stock_instrument_client=client
        )

        service.update_instrument_profile("INE002A01018")

        # Verified MongoDB upsert
        mongo_repo.upsert_one.assert_called_once()

        # Verified PostgreSQL upsert via UoW
        mock_unit_of_work.company_profiles_repository.upsert.assert_called_once()


