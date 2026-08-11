import time

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import StockInstrumentsClient
from apps.stock_data_management.infrastructure.db.repositories.company_profile_repostitory import CompanyProfileRepository
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_profile_repository import StockInstrumentsProfileRepository
from apps.stock_data_management.services.stock_instruments_service import StockInstrumentsService


class CompanyProfileService:
    def __init__(
        self,
        stock_instruments_service: StockInstrumentsService,
        company_profile_repository: CompanyProfileRepository,
        stock_instruments_profile_repository: StockInstrumentsProfileRepository,
        stock_instrument_client: StockInstrumentsClient
    ):

        self._stock_instruments_service = stock_instruments_service
        self._stock_instruments_profile_repository = stock_instruments_profile_repository
        self._company_profile_repository = company_profile_repository

        self._stock_instrument_client = stock_instrument_client

    # ---------------------------------
    # UPDATE INSTRUMENTS PROFILE
    # ---------------------------------

    def update_instruments_profile(
        self,
        batch_size=1000,
        sleep_time=0.2
    ):
        company_instruments_stream = self._stock_instruments_service.get_company_instruments_stream(
            batch_size)

        processed = 0
        failed = 0

        for instrument in company_instruments_stream:

            try:

                self.update_instrument_profile(
                    instrument.isin
                )

                processed += 1
                print(
                    f"Completed For :  {instrument.name} | {instrument.trading_symbol} | {instrument.instrument_key} | {instrument.isin}")
                if processed % 100 == 0:

                    print(
                        f"Processed: "
                        f"{processed}"
                    )

                time.sleep(sleep_time)

            except Exception as e:

                failed += 1

                message = (
                    f"Failed syncing "
                    f"{instrument.instrument_key}: "
                    f"{str(e)}"
                )

                print(message)

        print(
            f"Completed. "
            f"Processed={processed}, "
            f"Failed={failed}"
        )

    def update_instrument_profile(
        self,
        isin
    ):

        response = (
            self._stock_instrument_client
            .get_instrument_profile_from_upstox(
                isin
            )
        )
        print(response)
        if not response:

            return

        mongo_payload = (
            self._build_instrument_profile_payload(
                isin,
                response
            )
        )
        self._stock_instruments_profile_repository.upsert_one(
            {
                "isin":
                isin
            },
            mongo_payload
        )
        self._company_profile_repository.upsert(
            {
                "isin": isin,
                "sector": response.get("sector", None),
                "company_profile": response.get("company_profile", None)
            },
            ['isin']

        )

    def _build_instrument_profile_payload(
        self,
        isin,
        instrument_profile_data
    ):

        return {

            "isin":
            isin,

            "company_profile":
            instrument_profile_data.get(
                "company_profile"
            ),

            "sector":
            instrument_profile_data.get(
                "sector"
            ),

            "sector_market_cap_inr":
            instrument_profile_data.get(
                "sector_market_cap_inr"
            ),

            "sector_market_cap_usd":
            instrument_profile_data.get(
                "sector_market_cap_usd"
            ),
        }

    def update_instruments_profile_for_new_records(
        self,
        batch_size=1000,
        sleep_time=0.2
    ):
        company_instruments_stream = self._stock_instruments_service.get_company_instruments_stream(
            batch_size)
