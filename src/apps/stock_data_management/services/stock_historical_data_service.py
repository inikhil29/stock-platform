from datetime import date, datetime
import calendar
import json

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
                record_exists = uow.raw_historical_data_info_repository.find_one(
                    data
                )
                if not record_exists:
                    uow.raw_historical_data_info_repository.insert_one(
                        data=data
                    )

                else:
                    uow.raw_historical_data_info_repository.update_one(
                        data=data
                    )
            else:
                uow.raw_historical_data_info_repository.insert_one(
                    data=data
                )
