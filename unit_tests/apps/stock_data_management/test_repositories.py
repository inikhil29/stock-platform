"""
Unit tests for Stock Data Management specialized repositories and query repositories.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from apps.stock_data_management.infrastructure.db.queries_repositories.company_profile_queries import CompanyProfieQueries
from apps.stock_data_management.infrastructure.db.repositories.company_profile_repository import CompanyProfileRepository
from apps.stock_data_management.infrastructure.db.repositories.finance_data_source_repository import FinanceDataSourceRepository
from apps.stock_data_management.infrastructure.db.repositories.finance_metrics_repository import FinanceMetricsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_period_types_repository import FinancialPeriodTypesRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_report_price_units_repository import FinancialReportPriceUnitsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_statement_records_repository import FinancialStatementRecordsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_statements_repository import FinancialStatementRepository
from apps.stock_data_management.infrastructure.db.repositories.raw_historical_data_info_repository import StockRawHistoricalDataInfoRepository
from apps.stock_data_management.infrastructure.db.repositories.stock_candle_data_repository import StockCandleDataRepository
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_repository import StockInstrumentsRepository
from core.enum.candle_interval_enum import CandleInterval
from core.enum.finance_metrics_enum import FinancialMetric
from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.enum.financial_periods_enum import FinancialPeriod, StatementPeriodTypes
from core.enum.financial_quarter_enum import FinancialQuarter
from core.enum.financial_statement_type_enum import FinancialStatmentType
from core.enum.price_unit_enum import PriceUnitEnum


class TestAppRepositories:
    """Test suite for domain specific Postgres repositories."""

    def test_company_profile_check_if_record_exist(self, mock_db_session):
        mock_db_session.scalar.return_value = True
        repo = CompanyProfileRepository(mock_db_session)

        exists = repo.check_if_record_exist("INE002A01018")
        assert exists is True
        mock_db_session.scalar.assert_called_once()

    def test_finance_metrics_get_id_from_metric_code(self, mock_db_session):
        mock_db_session.scalar.return_value = 101
        repo = FinanceMetricsRepository(mock_db_session)

        metric_id = repo.get_id_from_metric_code(FinancialMetric.TOTAL_REVENUE)
        assert metric_id == 101

    def test_finance_data_source_upsert_and_get_id(self, mock_db_session):
        mock_db_session.scalar.return_value = 1
        repo = FinanceDataSourceRepository(mock_db_session)

        source_id = repo.upsert_and_get_id(FinancialDataSourceEnum.UPSTOX)
        assert source_id == 1

    def test_financial_period_types_upsert_and_get_id(self, mock_db_session):
        mock_db_session.scalar.return_value = 5
        repo = FinancialPeriodTypesRepository(mock_db_session)

        period_id = repo.upsert_and_get_id(
            financial_period_type=FinancialPeriod.Q,
            end_date=date(2023, 12, 31),
            quarter=FinancialQuarter.Q3
        )
        assert period_id == 5

    def test_financial_report_price_units_upsert_and_get_id(self, mock_db_session):
        mock_db_session.scalar.return_value = 2
        repo = FinancialReportPriceUnitsRepository(mock_db_session)

        unit_id = repo.upsert_and_get_id(PriceUnitEnum.CRORE)
        assert unit_id == 2

    def test_financial_statement_records_upsert_and_get_id(self, mock_db_session):
        mock_db_session.scalar.return_value = 99
        repo = FinancialStatementRecordsRepository(mock_db_session)

        record_id = repo.upsert_and_get_id(
            financial_statement_id=1,
            financial_period_type_id=5,
            finance_metric_id=101,
            value=Decimal("12345.67")
        )
        assert record_id == 99

    def test_financial_statements_upsert_and_get_id(self, mock_db_session):
        mock_db_session.scalar.return_value = 1
        repo = FinancialStatementRepository(mock_db_session)

        stmt_id = repo.upsert_and_get_id(
            finance_data_source_id=1,
            isin="INE002A01018",
            financial_report_price_unit_id=2,
            finance_statement_type=FinancialStatmentType.CONSOLIDATED,
            financial_statement_period_type=StatementPeriodTypes.YEARLY
        )
        assert stmt_id == 1

    def test_raw_historical_data_info_mark_as_processed(self, mock_db_session):
        mock_db_session.execute.return_value = MagicMock(rowcount=1)
        repo = StockRawHistoricalDataInfoRepository(mock_db_session)

        repo.mark_as_processed(42)
        mock_db_session.execute.assert_called_once()

    def test_raw_historical_data_info_mark_as_processed_not_found(self, mock_db_session):
        mock_db_session.execute.return_value = MagicMock(rowcount=0)
        repo = StockRawHistoricalDataInfoRepository(mock_db_session)

        with pytest.raises(ValueError, match="not found"):
            repo.mark_as_processed(999)

    def test_stock_instruments_fetch_keys_from_isin(self, mock_db_session):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["NSE_EQ|INE002A01018"]
        mock_db_session.scalars.return_value = mock_scalars

        repo = StockInstrumentsRepository(mock_db_session)
        keys = repo.fetch_instrument_keys_from_isin("INE002A01018")

        assert keys == ["NSE_EQ|INE002A01018"]

    def test_company_profile_queries_missing_stream(self, mock_db_session):
        mock_row = MagicMock()
        mock_db_session.scalars.return_value = [mock_row]

        queries = CompanyProfieQueries(mock_db_session)
        rows = list(queries.get_missing_companies_stream())

        assert len(rows) == 1
        assert rows[0] == mock_row

