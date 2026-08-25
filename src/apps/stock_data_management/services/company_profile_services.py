"""
Company Profile Service Module.

Coordinates fetching, formatting, and dual-persistence (PostgreSQL and MongoDB)
of corporate profile data, sector categorization, and market cap summaries.
"""

import logging
import time
from typing import Any

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import StockInstrumentsClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from apps.stock_data_management.infrastructure.db.repositories.company_profile_repository import CompanyProfileRepository
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_profile_repository import StockInstrumentsProfileRepository
from apps.stock_data_management.services.stock_instruments_service import StockInstrumentsService

logger = logging.getLogger(__name__)


class CompanyProfileService:
    """
    Service for syncing company fundamentals, business overview, sector,
    and market cap data from the Upstox API into MongoDB and PostgreSQL.

    Attributes:
        _stock_instruments_service (StockInstrumentsService): Service to stream instrument records.
        _stock_instruments_profile_repository (StockInstrumentsProfileRepository): MongoDB repo for JSON profiles.
        _unit_of_work (PostgresUnitOfWork): Unit of work for PostgreSQL persistence.
        _stock_instrument_client (StockInstrumentsClient): API client for fetching profile data from Upstox.
    """

    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_instruments_service: StockInstrumentsService,
        stock_instruments_profile_repository: StockInstrumentsProfileRepository,
        stock_instrument_client: StockInstrumentsClient
    ):
        """
        Initialize CompanyProfileService with database Unit of Work, repositories, and API clients.

        Parameters:
            unit_of_work (PostgresUnitOfWork): Unit of Work coordinating relational transactions.
            stock_instruments_service (StockInstrumentsService): Service providing stream of instruments.
            stock_instruments_profile_repository (StockInstrumentsProfileRepository): MongoDB repository.
            stock_instrument_client (StockInstrumentsClient): Client communicating with Upstox fundamentals API.
        """

        self._stock_instruments_service = stock_instruments_service
        self._stock_instruments_profile_repository = stock_instruments_profile_repository
        self._unit_of_work = unit_of_work
        self._stock_instrument_client = stock_instrument_client

    # ---------------------------------
    # UPDATE INSTRUMENTS PROFILE
    # ---------------------------------

    def update_instruments_profile(
        self,
        batch_size: int = 1000,
        sleep_time: float = 0.2
    ) -> None:
        """
        Iterate over instruments missing company profiles in PostgreSQL and fetch their details from Upstox.

        Streams unprofiled instruments, calls Upstox fundamentals endpoint for each ISIN,
        and saves structured and unstructured data to PostgreSQL and MongoDB respectively.

        Parameters:
            batch_size (int, optional): Batch size for database cursor streaming. Defaults to 1000.
            sleep_time (float, optional): Throttle delay in seconds between API requests to respect rate limits. Defaults to 0.2.
        """
        company_instruments_stream = self._stock_instruments_service.get_missing_companies_stream(
            batch_size
        )

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
        isin: str
    ) -> None:
        """
        Fetch company profile for a single ISIN from Upstox and update both MongoDB and PostgreSQL.

        1. Fetches fundamental profile JSON from Upstox.
        2. Upserts full JSON document into MongoDB `stock_instruments_profile` collection.
        3. Upserts relational summary (`isin`, `sector`, `company_profile`) into PostgreSQL `company_profile` table.

        Parameters:
            isin (str): 12-character International Securities Identification Number.
        """

        response = (
            self._stock_instrument_client
            .get_instrument_profile_from_upstox(
                isin
            )
        )
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
        with self._unit_of_work as uow:

            uow.company_profiles_repository.upsert(
                {
                    "isin": isin,
                    "sector": response.get("sector", None),
                    "company_profile": response.get("company_profile", None)
                },
                ['isin']

            )

    def _build_instrument_profile_payload(
        self,
        isin: str,
        instrument_profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Construct a normalized document dictionary for MongoDB storage.

        Parameters:
            isin (str): 12-character International Securities Identification Number.
            instrument_profile_data (dict[str, Any]): Raw JSON response from Upstox profile endpoint.

        Returns:
            dict[str, Any]: Formatted dictionary matching StockInstrumentsProfile MongoDB schema.
        """

        return {
            "isin": isin,
            "company_profile": instrument_profile_data.get("company_profile"),
            "sector": instrument_profile_data.get("sector"),
            "sector_market_cap_inr": instrument_profile_data.get("sector_market_cap_inr"),
            "sector_market_cap_usd": instrument_profile_data.get("sector_market_cap_usd"),
        }

    def update_instruments_profile_for_new_records(
        self,
        batch_size: int = 1000,
        sleep_time: float = 0.2
    ) -> None:
        """
        Iterate over all existing instruments with non-null ISINs and refresh their profile data.

        Parameters:
            batch_size (int, optional): Batch size for database cursor streaming. Defaults to 1000.
            sleep_time (float, optional): Throttle delay in seconds between API requests. Defaults to 0.2.
        """
        company_instruments_stream = self._stock_instruments_service.get_company_instruments_stream(
            batch_size=batch_size
        )

        processed = 0
        failed = 0

        for instrument in company_instruments_stream:
            if not instrument.isin:
                continue

            try:
                self.update_instrument_profile(
                    isin=instrument.isin
                )

                processed += 1
                print(
                    f"Completed For : {instrument.name} | {instrument.trading_symbol} | {instrument.instrument_key} | {instrument.isin}"
                )
                if processed % 100 == 0:
                    print(
                        f"Processed: {processed}"
                    )

                time.sleep(sleep_time)

            except Exception as e:
                failed += 1
                message = (
                    f"Failed syncing {instrument.instrument_key}: {str(e)}"
                )
                print(message)

        print(
            f"Completed. Processed={processed}, Failed={failed}"
        )
