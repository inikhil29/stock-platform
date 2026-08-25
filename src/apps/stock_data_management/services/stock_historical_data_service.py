"""
Stock Historical Data Service Module.

Orchestrates multi-resolution candlestick historical data ingestion from Upstox,
raw archive storage in AWS S3, metadata tracking in PostgreSQL, and bulk ingestion
of transformed candles into the time-series candle table.
"""

import calendar
from datetime import date, datetime
import json
import logging
from typing import Any, BinaryIO

from apps.stock_data_management.infrastructure.clients.stock_historical_data_client import StockHistoricalDataClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from apps.stock_data_management.infrastructure.db.repositories.raw_historical_data_info_repository import (
    StockRawHistoricalDataInfoRepository,
)
from core.clients.aws_client import AwsClient
from core.config.aws_settings import aws_settings
from core.enum.candle_interval_enum import CandleInterval
from core.utilities.printing_utilities import clear_line

logger = logging.getLogger(__name__)


class StockHistoricalDataService:
    """
    Service for downloading, archiving, and populating historical stock candlestick data.

    Manages chunking historical date ranges by month/year, querying Upstox API v3 candle endpoints,
    persisting raw responses into S3, logging batch ranges into `raw_historical_data_info`,
    and parsing/upserting millions of individual candle records into `stock_candle_data`.

    Attributes:
        _unit_of_work (PostgresUnitOfWork): Unit of Work coordinating database transactions.
        _stock_historical_data_client (StockHistoricalDataClient): Client for querying Upstox candle APIs.
        _aws_client (AwsClient): Client providing access to S3 storage operations.
    """

    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_historical_data_client: StockHistoricalDataClient,
        aws_client: AwsClient
    ):
        """
        Initialize the StockHistoricalDataService.

        Parameters:
            unit_of_work (PostgresUnitOfWork): Unit of Work for database session and repository management.
            stock_historical_data_client (StockHistoricalDataClient): Upstox HTTP client for historical candles.
            aws_client (AwsClient): AWS client wrapper for S3 bucket storage.
        """
        self._unit_of_work = unit_of_work
        self._stock_historical_data_client = stock_historical_data_client
        self._aws_client = aws_client

    def fetch_and_store_all_raw_historical_data_in_s3(
        self,
        instrument_key: str,
        interval: CandleInterval
    ) -> None:
        """
        Fetch full historical candle ranges for an instrument and archive raw JSON batches to AWS S3.

        Calculates earliest supported historical date boundary based on interval resolution
        (e.g., 2022 for intraday minutes, 2000 for daily/weekly/monthly). Checks last imported
        range in database to support incremental resumption, partitions date ranges into monthly
        or yearly blocks, downloads candles from Upstox, uploads to S3, and records range metadata.

        Parameters:
            instrument_key (str): Unique Upstox instrument identifier (e.g. 'NSE_EQ|INE002A01018').
            interval (CandleInterval): Resolution interval enum (e.g. CandleInterval.M1, CandleInterval.D1).

        Raises:
            Exception: If network, S3, or database errors occur during ingestion.
        """
        current_date = date.today()
        try:
            max_date_for_interval = self._get_max_date_limit_for_interval(
                interval=interval
            )
            with self._unit_of_work as uow:
                last_imported_date = self._get_last_imported_record_date(
                    repository=uow.raw_historical_data_info_repository,
                    instrument_key=instrument_key,
                    interval=interval
                )

            # If last imported date exists then continue import incrementally
            continue_import = False
            if last_imported_date:
                max_date_for_interval = last_imported_date
                continue_import = True

            by = 'm'
            if interval.unit not in ['minutes', 'hours']:
                by = 'y'

            get_month_range_list = self._generate_first_day_last_day_list(
                from_date=current_date,
                to_date=max_date_for_interval,
                by=by,
            )

            for i in get_month_range_list:
                from_date = str(i[0])
                to_date = str(i[1])
                print(
                    f"Processing for {instrument_key} from Date {from_date} - {to_date} : ", flush=True)
                print("\tRecord Fetching From Upstox ...", flush=True)
                get_records = self._fetch_historical_data(
                    instrument_key=instrument_key,
                    unit=interval.unit,
                    interval_option=interval.interval_option,
                    from_date=from_date,
                    to_date=to_date
                )
                clear_line()
                print("\tRecord Fetched From Upstox: Done", flush=True)
                storage_key = f"historical-data/{instrument_key}/{interval.value}/{from_date} - {to_date}"

                print("\tSaving Data in S3 ...", flush=True)
                self._store_historical_data_s3(get_records, storage_key)
                data = {
                    'instrument_key': instrument_key,
                    'interval': interval,
                    'from_date': datetime.strptime(from_date, "%Y-%m-%d").date(),
                    'to_date': datetime.strptime(to_date, "%Y-%m-%d").date(),
                }
                clear_line()
                print(
                    f"\tSaved Data in S3 with KEY | {storage_key} | : Done", flush=True)
                print("\tInserting record info to table ...", flush=True)
                self.insert_update_historical_data_info_report(
                    data=data, continue_import=continue_import)
                clear_line()
                print("\tInserted record info to table: Done", flush=True)
                clear_line()
                clear_line()
                clear_line()
                clear_line()
                print(
                    f"Processed for {instrument_key} from Date {from_date} - {to_date} : Done", flush=True)
                clear_line()
        except Exception as e:
            logger.exception(
                "Failed historical fetch for %s at interval %s: %s", instrument_key, interval.value, e)
            raise e

    def _store_historical_data_s3(
        self,
        data: Any,
        key: str
    ) -> None:
        """
        Serialize JSON payload and upload raw bytes to AWS S3 bucket.

        Parameters:
            data (Any): JSON-serializable candle response payload.
            key (str): S3 object key / path.
        """
        default_bucket = aws_settings.AWS_HISTORICAL_DATA_S3_BUCKET
        data_bytes = json.dumps(data).encode("utf-8")
        content_type = "application/json"
        s3_storage = self._aws_client.get_s3_storage()
        s3_storage.upload_bytes(default_bucket, key, data_bytes, content_type)

    def _get_historical_data_s3_stream(
        self,
        key: str
    ) -> BinaryIO | None:
        """
        Open a streaming context manager for an S3 object body.

        Parameters:
            key (str): S3 object key / path.

        Returns:
            BinaryIO | None: Streaming file-like context manager.
        """
        default_bucket = aws_settings.AWS_HISTORICAL_DATA_S3_BUCKET
        s3_storage = self._aws_client.get_s3_storage()
        return s3_storage.download_stream(default_bucket, key)

    def _fetch_historical_data(
        self,
        instrument_key: str,
        unit: str,
        interval_option: int,
        from_date: str,
        to_date: str
    ) -> dict[str, Any]:
        """
        Query Upstox API client for candle records within a specific date range.

        Parameters:
            instrument_key (str): Target instrument identifier.
            unit (str): Time unit string ('minutes', 'hours', 'days', 'weeks', 'months').
            interval_option (int): Numeric interval step (e.g. 1, 5, 15, 30).
            from_date (str): Start date string in 'YYYY-MM-DD' format.
            to_date (str): End date string in 'YYYY-MM-DD' format.

        Returns:
            dict[str, Any]: Upstox candle data dictionary containing 'candles' array.
        """
        result = self._stock_historical_data_client.get_historical_data_from_upstox(
            instrument_key=instrument_key,
            unit=unit,
            interval_option=interval_option,
            to_date=to_date,
            from_date=from_date
        )
        return result

    def _get_max_date_limit_for_interval(
        self,
        interval: CandleInterval
    ) -> date:
        """
        Determine the earliest supported start date for a given candle resolution.

        Intraday minute/hour intervals are limited to 2022-01-01 by Upstox historical retention.
        Daily/weekly/monthly intervals are supported back to 2000-01-01.

        Parameters:
            interval (CandleInterval): Candle resolution enum.

        Returns:
            date: Earliest available start date boundary.

        Raises:
            ValueError: If an unsupported unit or interval option is provided.
        """
        unit = interval.unit
        interval_option = interval.interval_option

        if unit == 'minutes':
            if 1 <= interval_option <= 300:
                return date(2022, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        if unit == 'hours':
            if 1 <= interval_option <= 5:
                return date(2022, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        if unit in ('days', 'weeks', 'months'):
            if interval_option == 1:
                return date(2000, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        raise ValueError(f"Invalid unit option {unit}")

    def _generate_first_day_last_day_list(
        self,
        from_date: date,
        to_date: date,
        by: str = 'm'
    ) -> list[tuple[date, date]]:
        """
        Partition a date span into a list of contiguous (start_of_period, end_of_period) date tuples.

        Parameters:
            from_date (date): Starting date (typically current date).
            to_date (date): Ending historical boundary date.
            by (str, optional): Partitioning frequency - 'm' for monthly chunks, 'y' for yearly chunks. Defaults to 'm'.

        Returns:
            list[tuple[date, date]]: List of (first_day, last_day) tuples spanning the period.
        """
        if from_date > to_date:
            high = to_date
            low = from_date
        else:
            high = from_date
            low = to_date

        res = []
        while high < low:
            first_day_month = last_day_month = high.month
            year = high.year
            if by == 'y':
                first_day_month = 1
                last_day_month = 12

            first_day = date(year, first_day_month, 1)

            _, last_day_of_month = calendar.monthrange(year, last_day_month)
            last_day = date(year, last_day_month, last_day_of_month)

            res.append((first_day, last_day))

            next_month = last_day_month % 12 + 1
            next_year = year + (last_day_month // 12)

            high = date(next_year, next_month, 1)

        return res

    def _get_last_imported_record_date(
        self,
        repository: StockRawHistoricalDataInfoRepository,
        instrument_key: str,
        interval: CandleInterval
    ) -> date | None:
        """
        Query the database to find the latest already-imported historical chunk end date.

        Parameters:
            repository (StockRawHistoricalDataInfoRepository): Historical metadata repository.
            instrument_key (str): Instrument key identifier.
            interval (CandleInterval): Target resolution interval.

        Returns:
            date | None: The latest `to_date` if previously imported, None otherwise.
        """
        result = repository.get_last_inserted_record_for_instrument_by_interval(
            instrument_key=instrument_key,
            interval=interval.value
        )
        if result:
            return result.to_date
        return None

    def insert_update_historical_data_info_report(
        self,
        data: dict[str, Any],
        continue_import: bool | None = None
    ) -> None:
        """
        Record historical range import metadata in the `raw_historical_data_info` table.

        Parameters:
            data (dict[str, Any]): Dictionary containing instrument_key, interval, from_date, and to_date.
            continue_import (bool | None, optional): If True, performs an upsert. If False, performs insert_one.
        """
        with self._unit_of_work as uow:
            if continue_import:
                uow.raw_historical_data_info_repository.upsert_and_get_id(
                    data=data
                )
            else:
                uow.raw_historical_data_info_repository.insert_one(
                    data=data
                )

    def insert_candle_data_from_s3(self) -> None:
        """
        Process unprocessed raw historical files from S3 and bulk-insert candle records into PostgreSQL.

        Iterates through all `raw_historical_data_info` rows with `processed_timestamp IS NULL`.
        For each batch:
        1. Streams raw JSON from S3.
        2. Parses individual candles: `[timestamp, open, high, low, close, volume, open_interest]`.
        3. Executes batch upserts into `stock_candle_data` in chunks of 5000 rows.
        4. Marks the `raw_historical_data_info` record as processed with current timestamp.
        """
        print("Started Importing...", flush=True)
        while True:
            records = []
            # --------------------------------
            # Get next unprocessed source row
            # --------------------------------
            with self._unit_of_work as uow:
                filter_condition = None
                if last_id:
                    filter_condition = uow.raw_historical_data_info_repository._model.id > last_id

                records = uow.raw_historical_data_info_repository.get_unprocessed_records(
                    filter=filter_condition,
                    batch_size=1000
                )
            if not records:
                break

            for record in records:
                storage_key = f"historical-data/{record.instrument_key}/{record.interval.value}/{record.from_date} - {record.to_date}"
                print(
                    f"\tStarting the process for key {storage_key} ", flush=True)
                source_record_id = record.id
                last_id = source_record_id

                # --------------------------------
                # S3 Stream & Parse
                # --------------------------------
                print("\t\tFetching data from S3 ...", flush=True)
                with self._get_historical_data_s3_stream(key=storage_key) as data_stream:
                    data = json.load(data_stream)
                clear_line()
                print("\t\tFetched data from S3: Done", flush=True)

                candle_records = data.get("candles", [])
                print(
                    f"\t\tTotal Records to be processed: {len(candle_records)}", flush=True)
                insert_records = []

                # --------------------------------
                # Transform + batch insert (5000)
                # --------------------------------
                for candle_record in candle_records:
                    candle_item = {
                        "raw_historical_data_info_id": source_record_id,
                        "candle_timestamp": candle_record[0],
                        "open": candle_record[1],
                        "high": candle_record[2],
                        "low": candle_record[3],
                        "close": candle_record[4],
                        "volume": candle_record[5],
                        "open_interest": candle_record[6],
                    }

                    insert_records.append(candle_item)
                    if len(insert_records) == 5000:
                        with self._unit_of_work as uow:
                            print("\t\tInserting the candle records...", flush=True)
                            uow.stock_candle_data_repository.make_bulk_upsert(
                                insert_records
                            )
                            insert_records = []
                            clear_line()
                            print(
                                "\t\tInserted the candle records: Done", flush=True)
                            clear_line()

                # --------------------------------
                # Final batch + mark processed
                # --------------------------------
                with self._unit_of_work as uow:
                    if insert_records:
                        print("\t\tInserting the candle records...", flush=True)
                        uow.stock_candle_data_repository.make_bulk_upsert(
                            insert_records
                        )
                        clear_line()
                        print("\t\tInserted the candle records: Done", flush=True)
                        clear_line()

                    print(
                        "\t\tUpdating the base table to mark as processed...", flush=True)
                    uow.raw_historical_data_info_repository.mark_as_processed(
                        record_id=source_record_id
                    )
                    clear_line()
                    print(
                        "\t\tUpdating the base table to mark as processed: Done", flush=True)
                    clear_line()

                clear_line()
                clear_line()
                clear_line()
