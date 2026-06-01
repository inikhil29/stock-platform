from apps.upstox.container import UpstoxContainer


def main():
    symbol = input("Enter the Treading: ").strip()
    upstox_instrument_container = UpstoxContainer()
    upstox_instrument_service = upstox_instrument_container.get_upstox_instrument_service()
    result= upstox_instrument_service.getInstrumentDetails(trading_symbol=symbol)
    print(result)


if __name__ == "__main__":
    main()

