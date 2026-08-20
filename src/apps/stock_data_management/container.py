
from apps.stock_data_management.infrastructure.clients.company_financial_data_client import CompanyFinancialDataClient
from apps.stock_data_management.infrastructure.clients.stock_historical_data_client import StockHistoricalDataClient
from apps.stock_data_management.infrastructure.db.mongodb import get_database
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_profile_repository import StockInstrumentsProfileRepository

from apps.stock_data_management.infrastructure.db.session import MySQLSessionFactory
from apps.stock_data_management.infrastructure.db.session import PostgresSessionFactory
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import (
    StockInstrumentsData
)

from apps.stock_data_management.infrastructure.db.models.instruments_profile import (
    StockInstrumentsProfile
)


from apps.stock_data_management.infrastructure.clients.upstox_client import (
    UpstoxClient
)

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import (
    StockInstrumentsClient
)

from apps.stock_data_management.services.company_finance_services import CompanyFinanceServices
from apps.stock_data_management.services.company_profile_services import CompanyProfileService
from apps.stock_data_management.services.stock_historical_data_service import StockHistoricalDataService
from apps.stock_data_management.services.stock_instruments_service import (
    StockInstrumentsService
)
from core.clients.aws_client import AwsClient


class StockDataManagementContainer:

    def __init__(self):

        self._aws_client = AwsClient()

        self._upstox_client = (
            UpstoxClient()
        )
        mongo_db = get_database()

        unit_of_work = PostgresUnitOfWork(PostgresSessionFactory)

        # Instrument Service Setup

        self._stock_instrument_client = (
            StockInstrumentsClient(
                self._upstox_client
            )
        )

        self._stock_instrument_service = (
            StockInstrumentsService(

                unit_of_work=(
                    unit_of_work
                ),

                stock_instrument_client=(
                    self._stock_instrument_client
                )
            )
        )

        # Historical Data Service Setup

        self._stock_historical_data_client = (
            StockHistoricalDataClient(
                self._upstox_client
            )
        )

        self._stock_historical_data_service = (
            StockHistoricalDataService(
                unit_of_work=(
                    unit_of_work
                ),
                stock_historical_data_client=self._stock_historical_data_client,
                aws_client=self._aws_client,
            )
        )

        # Company Profile setup

        self._stock_instruments_profile_repository = (
            StockInstrumentsProfileRepository(
                mongo_db, StockInstrumentsProfile
            )
        )

        self._company_profile_service = CompanyProfileService(
            unit_of_work=(
                unit_of_work
            ),
            stock_instruments_service=self._stock_instrument_service,
            stock_instruments_profile_repository=self._stock_instruments_profile_repository,
            stock_instrument_client=self._stock_instrument_client
        )

        # Financial Service Setup

        self._company_finance_data_client = CompanyFinancialDataClient(
            self._upstox_client
        )
        self._company_financial_data_service = CompanyFinanceServices(
            unit_of_work=(
                unit_of_work
            ),
            stock_instrument_client=self._company_finance_data_client
        )

    def get_stock_instrument_service(self):
        return self._stock_instrument_service

    def get_stock_historical_data_service(self):
        return self._stock_historical_data_service

    def get_company_profile_management_service(self):
        return self._company_profile_service

    def get_company_financial_data_service(self):
        return self._company_financial_data_service
