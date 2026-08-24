from apps.stock_data_management.container import (
    StockDataManagementContainer
)
from core.enum.candle_interval_enum import CandleInterval

isin = 'INE119A01028'

container = StockDataManagementContainer()

# Company Profile Update Process
print("Started Updating the profile details", flush=True)
company_profile_management_service = container.get_company_profile_management_service()

update_company_profile = company_profile_management_service.update_instrument_profile(
    isin=isin)
print("Profile Details Updated: Done", flush=True)

# Finance Data Process
print("Started Updating the finance details", flush=True)
finance_data_service = container.get_company_financial_data_service()

finance_data_service.parse_balance_sheet_from_upstox(
    isin
)
finance_data_service.parse_cash_flow_data_from_upstox(
    isin
)
finance_data_service.parse_income_statement_data_from_upstox(
    isin
)
print("Fnance Details Updated: Done", flush=True)

# Historical Data Update Process
print("Started Updating the Historical candle data", flush=True)

stock_instrument_service = container.get_stock_instrument_service()
instrument_keys_list = stock_instrument_service.fetch_instrument_keys_from_isin(
    isin=isin)
historical_data_service = container.get_stock_historical_data_service()
interval_list = [CandleInterval.M1, CandleInterval.D1, CandleInterval.W1]
for instrument_key in instrument_keys_list:
    
    for interval in interval_list:

        historical_data_service.fetch_and_store_all_raw_historical_data_in_s3(
            instrument_key=instrument_key, interval=interval)

historical_data_service.insert_candle_data_from_s3()
print("Historical candle data are Updated: Done", flush=True)
print("Done!!!")
