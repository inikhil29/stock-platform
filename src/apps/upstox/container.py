
from apps.upstox.infrastructure.clients.upstox_historical_data_client import UpstoxHistoricalDataClient
from apps.upstox.infrastructure.db.mongodb import get_database
from apps.upstox.models.raw_historical_data_info import RawHistoricalDataInfo
from apps.upstox.repositories.raw_historical_data_info_repository import UpstoxRawHistoricalDataInfoRepository
from apps.upstox.repositories.upstox_instrument_repository import UpstoxInstrumentRepository
from apps.upstox.repositories.upstox_instruments_profile_repository import UpstoxInstrumentsProfileRepository

from apps.upstox.infrastructure.db.session import MySQLSessionFactory
from apps.upstox.models.stock_instrument_data import (
    UpstoxInstrumentData
)

from apps.upstox.models.instruments_profile import (
    UpstoxInstrumentsProfile
)


from apps.upstox.infrastructure.clients.upstox_client import (
    UpstoxClient
)

from apps.upstox.infrastructure.clients.upstox_instruments_client import (
    UpstoxInstrumentsClient
)

from apps.upstox.services.upstox_historical_data_service import UpstoxHistoricalDataService
from apps.upstox.services.upstox_instrument_service import (
    UpstoxInstrumentsService
)
from core.clients.aws_client import AwsClient


class UpstoxContainer:

    def __init__(self):

        self._aws_client = AwsClient()

        self._upstox_client = (
            UpstoxClient()
        )
        mongo_db = get_database()

        #Instrument Service Setup

        self._upstox_instrument_repository = (
            UpstoxInstrumentRepository(
                MySQLSessionFactory,
                UpstoxInstrumentData,
            )
        )

        self._upstox_instruments_profile_repository = (
            UpstoxInstrumentsProfileRepository(
                mongo_db, UpstoxInstrumentsProfile
            )
        )

        self._upstox_instrument_client = (
            UpstoxInstrumentsClient(
                self._upstox_client
            )
        )

        self._upstox_instrument_service = (
            UpstoxInstrumentsService(

                upstox_instrument_repository=(
                    self._upstox_instrument_repository
                ),

                upstox_instruments_profile_repository=(
                    self._upstox_instruments_profile_repository
                ),

                upstox_instrument_client=(
                    self._upstox_instrument_client
                )
            )
        )

        #Historical Data Service Setup
        
        self._raw_historical_data_info_repository = (
            UpstoxRawHistoricalDataInfoRepository(
                MySQLSessionFactory,
                RawHistoricalDataInfo,
            )
        )

        self._upstox_historical_data_client = (
            UpstoxHistoricalDataClient(
                self._upstox_client
            )
        )

        self._upstox_historical_data_service = (
            UpstoxHistoricalDataService(
                raw_historical_data_info_repository=self._raw_historical_data_info_repository,
                upstox_historical_data_client=self._upstox_historical_data_client,
                aws_client=self._aws_client,
            )
        )

    def get_upstox_instrument_service(self):
        return self._upstox_instrument_service

    def get_upstox_historical_data_service(self):
        return self._upstox_historical_data_service
