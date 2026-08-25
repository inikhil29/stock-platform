"""
Stock Candle Data Repository Module.

Manages bulk ingestion and upserting of time-series candlestick data
(open, high, low, close, volume, open_interest) into PostgreSQL.
"""

from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.stock_candle_data import StockCandleData
from core.repositories.base_postgres_repository import BasePostgresRepository


class StockCandleDataRepository(BasePostgresRepository[StockCandleData]):
    """
    PostgreSQL repository for time-series `StockCandleData` records.

    Attributes:
        _model (type[StockCandleData]): Bound SQLAlchemy model class `StockCandleData`.
    """

    _model = StockCandleData

    def __init__(self, session: Session):
        """
        Initialize StockCandleDataRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def make_bulk_upsert(self, data: list[dict[str, Any]]) -> int:
        """
        Bulk upsert candlestick records matching composite unique key `(raw_historical_data_info_id, candle_timestamp)`.

        Parameters:
            data (list[dict[str, Any]]): List of candle dictionaries containing:
                - `raw_historical_data_info_id` (int): Source batch FK ID.
                - `candle_timestamp` (datetime): Timestamp of the candle.
                - `open` (float): Opening price.
                - `high` (float): Highest price.
                - `low` (float): Lowest price.
                - `close` (float): Closing price.
                - `volume` (int): Traded volume.
                - `open_interest` (int): Open interest.

        Returns:
            int: Number of rows inserted or updated.
        """
        unique_columns = [
            self._model.raw_historical_data_info_id,
            self._model.candle_timestamp,
        ]

        update_data = {
            self._model.updated_at: func.now()
        }

        return self.bulk_upsert(
            records=data,
            unique_columns=unique_columns,
            update_dict=update_data
        )
