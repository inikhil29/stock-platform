from sqlalchemy import func, select, text, update
from apps.stock_data_management.infrastructure.db.models.raw_historical_data_info import RawHistoricalDataInfo
from core.repositories.base_postgres_repository import BasePostgresRepository
from core.enum.candle_interval_enum import CandleInterval
from sqlalchemy.orm import Session


class StockRawHistoricalDataInfoRepository(
    BasePostgresRepository[RawHistoricalDataInfo]
):

    _model = RawHistoricalDataInfo

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def get_last_inserted_record_for_instrument_by_interval(self, instrument_key: str, interval: CandleInterval) -> RawHistoricalDataInfo | None:

        stmt = (select(self._model).where(self._model.instrument_key ==
                                          instrument_key, self._model.interval == interval).order_by(self._model.to_date.desc()).limit(1))

        res = self._session.scalar(statement=stmt)

        return res

    def get_unprocessed_records_strem(self, filter=None, batch_size: int | None = 1000):
        stmt = select(
            self._model
        ).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)

        result = self._session.scalars(
            stmt.execution_options(
                yield_per=batch_size
            )
        )

        for row in result:
            yield row

    def get_unprocessed_records(self, filter=None, batch_size: int | None = 1000):
        stmt = select(
            self._model
        ).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)

        result = self._session.scalars(
            stmt
        )

    def get_unprocessed_record(self, filter=None):
        stmt = select(
            self._model
        ).where(
            self._model.processed_timestamp.is_(None),
        )

        if filter is not None:
            stmt = stmt.where(filter)
            
        result = self._session.scalar(
            stmt.limit(1)
        )
        return result

    def mark_as_procesed(self, record_id: int):
        stmt = update(
            self._model
        ).where(
            self._model.id == record_id,
        ).values(
            processed_timestamp=func.now(),
        )

        execution_result = self._session.execute(
            stmt
        )
        if execution_result.rowcount == 0:
            raise ValueError(
                f"Raw historical record {record_id} not found"
            )
