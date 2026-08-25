"""
Raw Historical Data Info Repository Module.

Tracks historical candlestick download chunks, date range boundaries,
intervals, and ingestion status into the primary time-series tables in PostgreSQL.
"""

from typing import Any, Generator
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.raw_historical_data_info import RawHistoricalDataInfo
from core.enum.candle_interval_enum import CandleInterval
from core.repositories.base_postgres_repository import BasePostgresRepository


class StockRawHistoricalDataInfoRepository(BasePostgresRepository[RawHistoricalDataInfo]):
    """
    PostgreSQL repository for `RawHistoricalDataInfo` records.

    Attributes:
        _model (type[RawHistoricalDataInfo]): Bound SQLAlchemy model class `RawHistoricalDataInfo`.
    """

    _model = RawHistoricalDataInfo

    def __init__(self, session: Session):
        """
        Initialize StockRawHistoricalDataInfoRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(self, data: dict[str, Any]) -> int:
        """
        Upsert a historical batch metadata row and return its primary key ID.

        Unique constraint is evaluated on `(instrument_key, interval, from_date, to_date)`.
        Resets `processed_timestamp` to NULL on update to trigger re-ingestion if re-downloaded.

        Parameters:
            data (dict[str, Any]): Dictionary with keys `instrument_key`, `interval`, `from_date`, `to_date`.

        Returns:
            int: Primary key ID of the record.
        """
        insert_data = data

        unique_columns = [
            self._model.instrument_key,
            self._model.interval,
            self._model.from_date,
            self._model.to_date,
        ]

        update_data = {
            self._model.updated_at: func.now(),
            self._model.processed_timestamp: None
        }

        result = super()._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result

    def get_last_inserted_record_for_instrument_by_interval(
        self,
        instrument_key: str,
        interval: CandleInterval | str
    ) -> RawHistoricalDataInfo | None:
        """
        Retrieve the latest imported historical chunk (by `to_date` descending) for an instrument and interval.

        Parameters:
            instrument_key (str): Unique instrument identifier (e.g. 'NSE_EQ|INE002A01018').
            interval (CandleInterval | str): Target resolution interval enum or string value.

        Returns:
            RawHistoricalDataInfo | None: Latest historical record info row or None.
        """
        interval_val = interval.value if isinstance(
            interval, CandleInterval) else interval
        stmt = (
            select(self._model)
            .where(
                self._model.instrument_key == instrument_key,
                self._model.interval == interval_val
            )
            .order_by(self._model.to_date.desc())
            .limit(1)
        )

        res = self._session.scalar(statement=stmt)
        return res

    def get_unprocessed_records_stream(
        self,
        filter: Any = None,
        batch_size: int | None = 1000
    ) -> Generator[RawHistoricalDataInfo, None, None]:
        """
        Stream historical info records where `processed_timestamp IS NULL`.

        Parameters:
            filter (Any, optional): Additional SQL where-clause condition. Defaults to None.
            batch_size (int | None, optional): Server-side cursor batch size. Defaults to 1000.

        Yields:
            RawHistoricalDataInfo: Unprocessed record info model instance.
        """
        stmt = select(self._model).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)

        result = self._session.scalars(
            stmt.execution_options(yield_per=batch_size)
        )

        for row in result:
            yield row

    # Backward compatibility alias
    get_unprocessed_records_strem = get_unprocessed_records_stream

    def get_unprocessed_records(
        self,
        filter: Any = None,
        batch_size: int | None = 1000
    ) -> list[RawHistoricalDataInfo]:
        """
        Fetch a list of unprocessed historical info records.

        Parameters:
            filter (Any, optional): Additional SQL condition. Defaults to None.
            batch_size (int | None, optional): Maximum records to retrieve. Defaults to 1000.

        Returns:
            list[RawHistoricalDataInfo]: List of unprocessed record models.
        """
        stmt = select(self._model.id).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)

        if batch_size:
            stmt = stmt.limit(batch_size)

        result = self._session.scalars(stmt)
        return list(result.all())

    def get_unprocessed_record(self, filter: Any = None) -> RawHistoricalDataInfo | None:
        """
        Fetch a single unprocessed historical metadata row (`LIMIT 1`).

        Parameters:
            filter (Any, optional): Additional filter expression. Defaults to None.

        Returns:
            RawHistoricalDataInfo | None: Single unprocessed record or None.
        """
        stmt = select(self._model.id).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)

        result = self._session.scalar(stmt.limit(1))
        return result

    def mark_as_processed(self, record_id: int) -> None:
        """
        Mark a raw historical data record as processed by updating its `processed_timestamp` to current time.

        Parameters:
            record_id (int): Primary key ID of the `raw_historical_data_info` record.

        Raises:
            ValueError: If no record with the specified ID was found to update.
        """
        stmt = update(self._model).where(
            self._model.id == record_id,
        ).values(
            processed_timestamp=func.now(),
        )

        execution_result = self._session.execute(stmt)
        if execution_result.rowcount == 0:
            raise ValueError(f"Raw historical record {record_id} not found")
