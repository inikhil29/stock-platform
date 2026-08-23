from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.raw_historical_data_info import RawHistoricalDataInfo
from apps.stock_data_management.infrastructure.db.models.stock_candle_data import StockCandleData

class CandleDataQueries:
    def __init__(self, session:Session):
        self._session = session