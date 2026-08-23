from sqlalchemy.orm import sessionmaker, Session

from apps.stock_data_management.infrastructure.db.queries_repositories.company_profile_queries import CompanyProfieQueries
from apps.stock_data_management.infrastructure.db.repositories.company_profile_repository import (
    CompanyProfileRepository,
)
from apps.stock_data_management.infrastructure.db.repositories.finance_data_source_repository import FinanceDataSourceRepository
from apps.stock_data_management.infrastructure.db.repositories.finance_metrics_repository import FinanceMetricsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_period_types_repository import FinancialPeriodTypesRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_report_price_units_repository import FinancialReportPriceUnitsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_statement_records_repository import FinancialStatementRecordsRepository
from apps.stock_data_management.infrastructure.db.repositories.financial_statements_repository import FinancialStatementRepository
from apps.stock_data_management.infrastructure.db.repositories.raw_historical_data_info_repository import (
    StockRawHistoricalDataInfoRepository,
)
from apps.stock_data_management.infrastructure.db.repositories.stock_candle_data_repository import StockCandleDataRepository
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_repository import (
    StockInstrumentsRepository,
)


class PostgresUnitOfWork:

    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory

    def __enter__(self):
        self._session = self._session_factory()

        # ---------------------------------
        # MODEL REPOSITORIES
        # ---------------------------------

        self.stock_instruments_repository = StockInstrumentsRepository(
            self._session
        )

        self.company_profiles_repository = CompanyProfileRepository(
            self._session
        )

        self.raw_historical_data_info_repository = (
            StockRawHistoricalDataInfoRepository(
                self._session
            )
        )

        self.stock_candle_data_repository = (
            StockCandleDataRepository(
                self._session
            )
        )

        self.finance_metrics_repository = (
            FinanceMetricsRepository(
                self._session
            )
        )

        self.finace_data_source_repository = (
            FinanceDataSourceRepository(
                self._session
            )
        )

        self.financial_period_types_repository = (
            FinancialPeriodTypesRepository(
                self._session
            )
        )

        self.financial_report_price_units_repository = (
            FinancialReportPriceUnitsRepository(
                self._session
            )
        )

        self.financial_statement_records_repository = (
            FinancialStatementRecordsRepository(
                self._session
            )
        )

        self.financial_statements_repository = (
            FinancialStatementRepository(
                self._session
            )
        )

        # ---------------------------------
        # QUERY REPOSITORIES
        # ---------------------------------
        self.company_profile_queries_repository = (
            CompanyProfieQueries(
                self._session
            )
        )
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            self._session.close()
            self._session = None

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
