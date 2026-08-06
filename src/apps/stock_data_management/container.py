
from apps.stock_data_management.infrastructure.clients.stock_historical_data_client import StockHistoricalDataClient
from apps.stock_data_management.infrastructure.db.mongodb import get_database
from apps.stock_data_management.models.raw_historical_data_info import RawHistoricalDataInfo
from apps.stock_data_management.repositories.raw_historical_data_info_repository import StockRawHistoricalDataInfoRepository
from apps.stock_data_management.repositories.stock_instruments_repository import StockInstrumentsRepository
from apps.stock_data_management.repositories.stock_instruments_profile_repository import StockInstrumentsProfileRepository

from apps.stock_data_management.infrastructure.db.session import MySQLSessionFactory
from apps.stock_data_management.infrastructure.db.session import PostgresSessionFactory
from apps.stock_data_management.models.stock_instruments_data import (
    StockInstrumentsData
)

from apps.stock_data_management.models.instruments_profile import (
    StockInstrumentsProfile
)


from apps.stock_data_management.infrastructure.clients.upstox_client import (
    UpstoxClient
)

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import (
    StockInstrumentsClient
)

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

        #Instrument Service Setup

        self._stock_instruments_repository = (
            StockInstrumentsRepository(
                PostgresSessionFactory,
                StockInstrumentsData,
            )
        )

        self._stock_instruments_profile_repository = (
            StockInstrumentsProfileRepository(
                mongo_db, StockInstrumentsProfile
            )
        )

        self._stock_instrument_client = (
            StockInstrumentsClient(
                self._upstox_client
            )
        )

        self._stock_instrument_service = (
            StockInstrumentsService(

                stock_instruments_repository=(
                    self._stock_instruments_repository
                ),

                stock_instruments_profile_repository=(
                    self._stock_instruments_profile_repository
                ),

                stock_instrument_client=(
                    self._stock_instrument_client
                )
            )
        )

        #Historical Data Service Setup
        
        self._raw_historical_data_info_repository = (
            StockRawHistoricalDataInfoRepository(
                PostgresSessionFactory,
                RawHistoricalDataInfo,
            )
        )

        self._stock_historical_data_client = (
            StockHistoricalDataClient(
                self._upstox_client
            )
        )

        self._stock_historical_data_service = (
            StockHistoricalDataService(
                raw_historical_data_info_repository=self._raw_historical_data_info_repository,
                stock_historical_data_client=self._stock_historical_data_client,
                aws_client=self._aws_client,
            )
        )

    def get_stock_instrument_service(self):
        return self._stock_instrument_service

    def get_stock_historical_data_service(self):
        return self._stock_historical_data_service
