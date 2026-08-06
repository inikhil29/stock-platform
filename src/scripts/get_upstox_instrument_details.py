from apps.stock_data_management.container import StockDataManagementContainer


def main():
    symbol = input("Enter the Treading: ").strip()
    stock_data_management_container = StockDataManagementContainer()
    stock_instrument_service = stock_data_management_container.get_stock_instrument_service()
    result= stock_instrument_service.getInstrumentDetails(trading_symbol=symbol)
    print(result)


if __name__ == "__main__":
    main()

