"""
Unit tests for CompanyFinanceServices.
"""

from unittest.mock import MagicMock
import pytest

from apps.stock_data_management.config.finance_matrics_alias_mapping import FINANCIAL_METRIC_ALIASES
from apps.stock_data_management.config.finance_units_alias_mapping import FINANCIAL_PRICE_UNITS_ALIASES
from apps.stock_data_management.services.company_finance_services import CompanyFinanceServices
from core.enum.finance_metrics_enum import FinancialMetric
from core.enum.price_unit_enum import PriceUnitEnum


class TestCompanyFinanceServices:
    """Test suite for CompanyFinanceServices financial statement transformations."""

    def test_metric_alias_mapping(self):
        assert FINANCIAL_METRIC_ALIASES.get("Total Revenue") == FinancialMetric.TOTAL_REVENUE
        assert "Non-existent Metric" not in FINANCIAL_METRIC_ALIASES

    def test_price_unit_alias_mapping(self):
        assert FINANCIAL_PRICE_UNITS_ALIASES.get("crore") == PriceUnitEnum.CRORE

    def test_parse_balance_sheet_from_upstox(self, mock_unit_of_work):
        client = MagicMock()
        client.get_balance_sheet_from_upstox.return_value = {
            "type": "consolidated",
            "time_period": "yearly",
            "units_in": "crore",
            "history": [
                {"total_asset": 1950121, "total_liability": 940495, "period": "Mar 2025"},
                {"total_asset": 1755986, "total_liability": 830198, "period": "Mar 2024"}
            ],
            "full_statement": [
                {
                    "particular": "Non-Current Assets",
                    "history": [
                        {"period": "Mar 2025", "value": 1450851},
                        {"period": "Mar 2024", "value": 1285886}
                    ]
                },
                {
                    "particular": "Total Assets",
                    "history": [
                        {"period": "Mar 2025", "value": 1950121},
                        {"period": "Mar 2024", "value": 1755986}
                    ]
                }
            ]
        }

        mock_unit_of_work.finace_data_source_repository.upsert_and_get_id.return_value = 1
        mock_unit_of_work.financial_report_price_units_repository.upsert_and_get_id.return_value = 2
        mock_unit_of_work.financial_statements_repository.upsert_and_get_id.return_value = 3
        mock_unit_of_work.finance_metrics_repository.upsert_and_get_id.return_value = 4
        mock_unit_of_work.financial_period_types_repository.upsert_and_get_id.return_value = 5

        service = CompanyFinanceServices(mock_unit_of_work, client)
        service.parse_balance_sheet_from_upstox("INE002A01018")

        client.get_balance_sheet_from_upstox.assert_called_once_with(
            isin="INE002A01018",
            type="consolidated"
        )
        assert mock_unit_of_work.financial_statement_records_repository.upsert_and_get_id.call_count >= 2

    def test_parse_income_statement_data_from_upstox(self, mock_unit_of_work):
        client = MagicMock()
        client.get_income_statement_from_upstox.return_value = {
            "type": "consolidated",
            "time_period": "yearly",
            "units_in": "crore",
            "income_statement": [
                {
                    "category": "revenue",
                    "history": [
                        {"value": 982671, "period": "Mar 2025", "change": "+7.15%"}
                    ]
                }
            ],
            "full_statement": [
                {
                    "particular": "Total Revenue",
                    "history": [
                        {"period": "Mar 2025", "value": 982671}
                    ]
                }
            ]
        }

        mock_unit_of_work.finace_data_source_repository.upsert_and_get_id.return_value = 1
        mock_unit_of_work.financial_report_price_units_repository.upsert_and_get_id.return_value = 2
        mock_unit_of_work.financial_statements_repository.upsert_and_get_id.return_value = 3
        mock_unit_of_work.finance_metrics_repository.upsert_and_get_id.return_value = 4
        mock_unit_of_work.financial_period_types_repository.upsert_and_get_id.return_value = 5

        service = CompanyFinanceServices(mock_unit_of_work, client)
        service.parse_income_statement_data_from_upstox("INE002A01018")

        client.get_income_statement_from_upstox.assert_called_once_with(
            isin="INE002A01018",
            type="consolidated",
            time_period="quarterly"
        )
        assert mock_unit_of_work.financial_statement_records_repository.upsert_and_get_id.call_count >= 1


