from pathlib import Path

from apps.stock_data_management.container import (
    StockDataManagementContainer
)
from core.enum.candle_interval_enum import CandleInterval

BASE_DIR = (
    Path(__file__).resolve().parent
)


instrument_key = 'NSE_EQ|INE119A01028'
interval = CandleInterval.D1

stock_data_management_container = StockDataManagementContainer()
historical_data_service = stock_data_management_container.get_stock_historical_data_service()
historical_data_service.fetch_and_store_all_raw_historical_data_in_s3(instrument_key=instrument_key, interval=interval)