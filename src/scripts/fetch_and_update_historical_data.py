from pathlib import Path

from apps.upstox.container import (
    UpstoxContainer
)
from core.utilities.candle_interval import CandleInterval

BASE_DIR = (
    Path(__file__).resolve().parent
)


instrument_key = 'BSE_EQ|INE0KCE01017'
interval = CandleInterval.M1

upstox_container = UpstoxContainer()
historical_data_service = upstox_container.get_upstox_historical_data_service()
historical_data_service.fetch_and_store_all_raw_historical_data_in_s3_by_month(instrument_key=instrument_key, interval=interval)