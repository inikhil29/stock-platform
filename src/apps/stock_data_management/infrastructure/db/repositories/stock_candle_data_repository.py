from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.stock_candle_data import StockCandleData
from core.repositories.base_postgres_repository import BasePostgresRepository


class StockCandleDataRepository(
    BasePostgresRepository[StockCandleData]
):
    _model = StockCandleData

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )
