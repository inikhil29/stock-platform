from sqlalchemy import func, select, text
from apps.stock_data_management.infrastructure.db.models.raw_historical_data_info import RawHistoricalDataInfo
from core.repositories.base_postgres_repository import BasePostgresRepository
from core.enum.candle_interval import CandleInterval
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
