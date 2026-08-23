from sqlalchemy import func, select, exists
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

    def make_bulk_upsert(self, data):
        unique_columns = [
            self._model.raw_historical_data_info_id,
            self._model.candle_timestamp,
        ]

        update_data = {
            self._model.updated_at: func.now()
        }

        self.bulk_upsert(
            records=data,
            unique_columns=unique_columns,
            update_dict=update_data
        )
