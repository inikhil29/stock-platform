from pathlib import Path

from apps.stock_info.container import (
    UpstoxContainer
)
from core.enum.candle_interval import CandleInterval

BASE_DIR = (
    Path(__file__).resolve().parent
)


instrument_key = 'NSE_EQ|INE0KCE01017'
interval = CandleInterval.D1

upstox_container = UpstoxContainer()
historical_data_service = upstox_container.get_upstox_historical_data_service()
historical_data_service.fetch_and_store_all_raw_historical_data_in_s3(instrument_key=instrument_key, interval=interval)