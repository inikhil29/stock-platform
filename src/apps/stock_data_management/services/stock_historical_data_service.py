from datetime import date, datetime
import calendar
import json
from typing import BinaryIO

from apps.stock_data_management.infrastructure.clients.stock_historical_data_client import StockHistoricalDataClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from apps.stock_data_management.infrastructure.db.repositories.raw_historical_data_info_repository import StockRawHistoricalDataInfoRepository
from core.clients.aws_client import AwsClient
from core.enum.candle_interval_enum import CandleInterval
from core.config.aws_settings import aws_settings
from core.utilities.printing_utilities import clear_line


class StockHistoricalDataService:
    def __init__(self, unit_of_work: PostgresUnitOfWork, stock_historical_data_client: StockHistoricalDataClient, aws_client: AwsClient):
        self._unit_of_work = unit_of_work
        self._stock_historical_data_client = stock_historical_data_client
        self._aws_client = aws_client

    def fetch_and_store_all_raw_historical_data_in_s3(self, instrument_key: str, interval: CandleInterval) -> None:
        current_date = date.today()
        try:

            max_date_for_interval = self._get_max_date_limit_for_interval(
                interval)
            with self._unit_of_work as uow:
                last_imported_date = self._get_last_imported_record_date(
                    repository=uow.raw_historical_data_info_repository,
                    instrument_key=instrument_key,
                    interval=interval
                )

            # If last imported date exists then make import as continue
            continue_import = False
            if last_imported_date:
                max_date_for_interval = last_imported_date
                continue_import = True
            by = 'm'
            if interval.unit not in ['minutes', 'hours']:
                by = 'y'

            get_month_range_list = self._generate_first_day_last_day_list(
                current_date,
                max_date_for_interval,
                by,
            )

            for i in get_month_range_list:
                from_date = str(i[0])
                to_date = str(i[1])
                print(
                    f"Processing for {instrument_key} from Date {from_date} - {to_date} : ", flush=True)
                print(f"\tRecord Fetching From Upstox ...", flush=True)
                get_records = (self._fetch_historical_data(
                    instrument_key=instrument_key,
                    unit=interval.unit,
                    interval_option=interval.interval_option,
                    from_date=from_date,
                    to_date=to_date
                ))
                clear_line()
                print(f"\tRecord Fetched From Upstox: Done", flush=True)
                storage_key = f"historical-data/{instrument_key}/{interval.value}/{from_date} - {to_date}"

                print(f"\tSaving Data in S3 ...", flush=True)
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
                print(f"\tInserting record info to table ...", flush=True)
                self.insert_update_historical_data_info_report(
                    data=data, continue_import=continue_import)
                clear_line()
                print(f"\tInserted record info to table: Done", flush=True)
                clear_line()
                clear_line()
                clear_line()
                clear_line()
                print(
                    f"Processed for {instrument_key} from Date {from_date} - {to_date} : Done", flush=True)
                clear_line()

            print("Done!!")
        except Exception as e:
            raise e

    def _store_historical_data_s3(self, data, key: str) -> None:
        default_bucket = aws_settings.AWS_HISTORICAL_DATA_S3_BUCKET
        data = json.dumps(data).encode("utf-8")
        content_type = "application/json"
        s3_storage = self._aws_client.get_s3_storage()
        s3_storage.upload_bytes(default_bucket, key, data, content_type)

    def _get_historical_data_s3_stream(self, key: str) -> BinaryIO | None:
        default_bucket = aws_settings.AWS_HISTORICAL_DATA_S3_BUCKET
        s3_storage = self._aws_client.get_s3_storage()
        return s3_storage.download_stream(default_bucket, key)

    def _fetch_historical_data(self, instrument_key, unit, interval_option, from_date, to_date):
        result = self._stock_historical_data_client.get_historical_data_from_upstox(
            instrument_key,
            unit,
            interval_option,
            to_date,
            from_date
        )
        return result

    def _get_max_date_limit_for_interval(self, interval: CandleInterval) -> date:
        unit = interval.unit
        interval_option = interval.interval_option

        if unit == 'minutes':
            if interval_option >= 1 and interval_option <= 300:
                return date(2022, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        if unit == 'hours':
            if interval_option >= 1 and interval_option <= 5:
                return date(2022, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        if unit == 'days':
            if interval_option == 1:
                return date(2000, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")
        if unit == 'weeks':
            if interval_option == 1:
                return date(2000, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        if unit == 'months':
            if interval_option == 1:
                return date(2000, 1, 1)
            else:
                raise ValueError(f"Invalid interval option {interval_option}")

        raise ValueError(f"Invalid unit option {unit}")

    def _generate_first_day_last_day_list(self, from_date: date, to_date: date, by: str = 'm') -> list[tuple[date, date]]:
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

    def _get_last_imported_record_date(self, repository: StockRawHistoricalDataInfoRepository, instrument_key: str, interval: CandleInterval) -> date | None:

        result = repository.get_last_inserted_record_for_instrument_by_interval(
            instrument_key=instrument_key, interval=interval.value)
        if result:
            return result.to_date
        return None

    def insert_update_historical_data_info_report(self, data, continue_import: bool | None = None) -> None:
        with self._unit_of_work as uow:

            if continue_import:

                record_id = uow.raw_historical_data_info_repository.upsert_and_get_id(
                    data
                )
            else:
                uow.raw_historical_data_info_repository.insert_one(
                    data=data
                )

    def insert_candle_data_from_s3(self):
        filter = None
        last_id = None
        print("Started Importing...")
        while True:
            record = None
            with self._unit_of_work as uow:
                if last_id:
                    filter = self._unit_of_work.raw_historical_data_info_repository._model.id > last_id
                record = uow.raw_historical_data_info_repository.get_unprocessed_record(
                    filter=filter)

            if not record:
                break

            storage_key = f"historical-data/{record.instrument_key}/{record.interval.value}/{record.from_date} - {record.to_date}"
            print(f"\tStarting the process for key {storage_key} ", flush=True)
            last_id = record.id
            print(f"\t\tFetching data from S3 ...", flush=True)
            with self._get_historical_data_s3_stream(key=storage_key) as data_stream:
                data = json.load(data_stream)
            clear_line()
            print(
                f"\t\tFetched data from S3: Done", flush=True)

            candle_records = data.get("candles", [])
            print(
                f"\t\tTotal Records to be processed: {len(candle_records)}", flush=True)
            insert_records = []
            if candle_records and len(candle_records) > 0:
                for candle_record in candle_records:
                    print(
                        f"\t\tProcessing for candle record: {candle_record}", flush=True)
                    record = {
                        "raw_historical_data_info_id": last_id,
                        "candle_timestamp": candle_record[0],
                        "open": candle_record[1],
                        "high": candle_record[2],
                        "low": candle_record[3],
                        "close": candle_record[4],
                        "volume": candle_record[5],
                        "open_interest": candle_record[6],
                    }

                    insert_records.append(record)
                    clear_line()
            with self._unit_of_work as uow:
                if insert_records:

                    print(
                        f"\t\tInserting the candle records...", flush=True)
                    uow.stock_candle_data_repository.make_bulk_upsert(
                        insert_records,)
                    clear_line()
                    print(
                        f"\t\tInserting the candle records: Done", flush=True)
                    clear_line()

                print(
                    f"\t\tUpdating the base table to mark as processed...", flush=True)
                uow.raw_historical_data_info_repository.mark_as_procesed(
                    last_id)
                clear_line()
                print(
                    f"\t\tUpdating the base table to mark as processed: Done", flush=True)

                clear_line()

            clear_line()
            clear_line()
            clear_line()
        print("Done!")
