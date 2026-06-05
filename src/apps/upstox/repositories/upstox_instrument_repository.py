from apps.upstox.infrastructure.db.session import SessionFactory
from apps.upstox.models.stock_instrument_data import (
    UpstoxStockInstrumentData
)
from core.repositories.base_mysql_repository import BaseMySQLRepository


class UpstoxInstrumentRepository(
    BaseMySQLRepository
):

    def __init__(self):

        super().__init__(
            model=UpstoxStockInstrumentData,
            session_factory=SessionFactory
        )
