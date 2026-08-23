from pathlib import Path

from apps.stock_data_management.container import (
    StockDataManagementContainer
)
from core.enum.candle_interval_enum import CandleInterval

BASE_DIR = (
    Path(__file__).resolve().parent
)

stock_data_management_container = StockDataManagementContainer()
historical_data_service = stock_data_management_container.get_stock_historical_data_service()
historical_data_service.insert_candle_data_from_s3()