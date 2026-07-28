
from apps.upstox.infrastructure.db.mongodb import get_database
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

from apps.upstox.services.upstox_instrument_service import (
    UpstoxInstrumentsService
)


class UpstoxContainer:

    def __init__(self):

        self._upstox_instrument_repository = (
            UpstoxInstrumentRepository(
                UpstoxInstrumentData, MySQLSessionFactory)
        )

        mongo_db = get_database()

        self._upstox_instruments_profile_repository = (
            UpstoxInstrumentsProfileRepository(
                mongo_db, UpstoxInstrumentsProfile
            )
        )

        self._upstox_client = (
            UpstoxClient()
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

    def get_upstox_instrument_service(self):
        return self._upstox_instrument_service
