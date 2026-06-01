import ijson
import pandas as pd
import time

from apps.upstox.infrastructure.clients.upstox_instruments_client import UpstoxInstrumentsClient
from apps.upstox.repositories.upstox_instrument_repository import UpstoxInstrumentRepository
from apps.upstox.repositories.upstox_instruments_profile_repository import UpstoxInstrumentsProfileRepository


class UpstoxInstrumentsService:

    def __init__(
        self,
        upstox_instrument_repository: UpstoxInstrumentRepository,
        upstox_instruments_profile_repository: UpstoxInstrumentsProfileRepository,
        upstox_instrument_client: UpstoxInstrumentsClient
    ):

        self._upstox_instrument_repository = upstox_instrument_repository
        self._upstox_instrument_repository_valid_columns = self._upstox_instrument_repository.get_valid_columns()
        self._upstox_instruments_profile_repository = upstox_instruments_profile_repository

        self._upstox_instrument_client = upstox_instrument_client

    # ---------------------------------
    # PROCESS FILE
    # ---------------------------------

    def sync_instruments(
        self,
        json_file_path,
        batch_size=10
    ):

        batch = []

        with open(
            json_file_path,
            "rb"
        ) as json_file:

            records = ijson.items(
                json_file,
                "item"
            )

            for row_number, row in enumerate(
                records,
                start=1
            ):

                try:

                    transformed = (
                        self._transform_record(
                            row,
                            self._upstox_instrument_repository_valid_columns
                        )
                    )

                    if not transformed:
                        continue

                    batch.append(
                        transformed
                    )

                    if len(batch) >= batch_size:

                        self._process_batch(
                            batch
                        )

                        batch.clear()

                except Exception as e:

                    print(
                        f"Error row "
                        f"{row_number}: {e}"
                    )

            if batch:

                self._process_batch(batch)

    # ---------------------------------
    # TRANSFORM RECORD
    # ---------------------------------
    def _transform_record(
        self,
        row,
        valid_columns
    ):

        filtered = {

            k: v

            for k, v in row.items()

            if k in valid_columns
        }

        if not filtered:
            return None

        filtered = (
            pd.Series(filtered)
            .astype(object)
            .reindex(valid_columns)
        )

        filtered = filtered.where(
            pd.notnull(filtered),
            None
        )

        return filtered.to_dict()

    # ---------------------------------
    # PROCESS BATCH
    # ---------------------------------
    def _process_batch(
        self,
        batch
    ):

        print(
            f"Processing batch: {batch}"
            f"{len(batch)}"
        )

        count = (
            self._upstox_instrument_repository.bulk_upsert(
                batch
            )
        )

        print(
            f"Inserted/Updated: "
            f"{count}"
        )

    # ---------------------------------
    # UPDATE INSTRUMENTS PROFILE
    # ---------------------------------

    def update_instruments_profile(
        self,
        batch_size=1000,
        sleep_time=0.2
    ):

        conditions = [
            self._upstox_instrument_repository.model.isin.isnot(None),
            self._upstox_instrument_repository.model.isin != ''

        ]
        instruments = (
            self._upstox_instrument_repository
            .stream(
                batch_size=batch_size,
                conditions=conditions
            )
        )

        processed = 0
        failed = 0

        for instrument in instruments:

            try:

                self._upadate_single_instrument_profile(
                    instrument
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

    def _upadate_single_instrument_profile(
        self,
        instrument
    ):

        response = (
            self._upstox_instrument_client
            .get_instrument_profile(
                instrument.isin
            )
        )
        if not response:

            return

        mongo_payload = (
            self._build_instrument_profile_payload(
                instrument,
                response
            )
        )
        self._upstox_instruments_profile_repository.upsert_one(
            {
                "instrument_id":
                instrument.id,
                "instrument_key":
                instrument.instrument_key
            },
            mongo_payload
        )
        self._upstox_instrument_repository.update_one(
            {
                "id": instrument.id
            },
            {
                "sector": response.get("sector", None),
                "company_profile": response.get("company_profile", None)
            }

        )

    def _build_instrument_profile_payload(
        self,
        instrument_data,
        instrument_profile_data
    ):

        return {

            "instrument_id":
            instrument_data.id,

            "instrument_key":
            instrument_data.instrument_key,

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

    def getInstrumentDetails(self, trading_symbol=None, isin=None):

        filters = {}

        if trading_symbol:
            filters["trading_symbol"] = trading_symbol

        if isin:
            filters["isin"] = isin

        result = self._upstox_instrument_repository.find_one(
            filters=filters
        )

        return result
