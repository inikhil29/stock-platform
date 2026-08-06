from sqlalchemy import func, select, text
from apps.stock_data_management.models.raw_historical_data_info import RawHistoricalDataInfo
from core.repositories.base_postgres_repository import BasePostgresRepository
from core.enum.candle_interval import CandleInterval
from sqlalchemy.orm import Session, sessionmaker



class StockRawHistoricalDataInfoRepository(
    BasePostgresRepository
):

    def __init__(self, session_factory:sessionmaker[Session], model: RawHistoricalDataInfo):

        super().__init__(
            model=model,
            session_factory=session_factory
        )

    def get_last_inserted_record_for_instrument_by_inerval(self, instrument_key: str, interval: CandleInterval) -> RawHistoricalDataInfo | None:
        with self.session_factory() as session:

            stmt = (select(self.model).where(self.model.instrument_key ==
                                            instrument_key, self.model.interval == interval).order_by(self.model.to_date.desc()).limit(1))
            
            res = session.scalar(statement=stmt)
            
            return res
