from apps.stock_info.container import UpstoxContainer


upstox_instrument_container = UpstoxContainer()
upstox_instrument_service = upstox_instrument_container.get_upstox_instrument_service()


upstox_instrument_service.update_instruments_profile(batch_size=100)