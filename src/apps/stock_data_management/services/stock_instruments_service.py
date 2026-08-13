from datetime import datetime
from uuid import uuid4

import ijson
import pandas as pd
import time

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import StockInstrumentsClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_repository import StockInstrumentsRepository

from core.dataframe.engines.polars.reader import PolarsReader
from core.dataframe.engines.polars.schema_validator import PolarsSchemaValidator
from pathlib import Path
from core.config.paths import DATA_DIR


class StockInstrumentsService:

    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_instrument_client: StockInstrumentsClient
    ):

        self._unit_of_work = unit_of_work
        with self._unit_of_work as uow:
            self._stock_instruments_valid_columns = uow.stock_instruments_repository.get_valid_columns()

        self._stock_instrument_client = stock_instrument_client

    # ---------------------------------
    # PROCESS FILE
    # ---------------------------------

    def sync_instruments(
        self,
        json_file_path,
        batch_size=1000
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
                            self._stock_instruments_valid_columns
                        )
                    )

                    if not transformed:
                        continue

                    batch.append(
                        transformed
                    )

                    if len(batch) >= batch_size:

                        self.process_batch(
                            batch
                        )

                        batch.clear()
                except Exception as e:

                    print(
                        f"Error row "
                        f"{row_number}: {e}"
                    )
                    quit()

    def sync_instruments_new(self, json_file_path):
        polars_reader = PolarsReader()
        dataframe = polars_reader.read_json(
            json_file_path, infer_schema_length=None)

        polar_schema_validator = PolarsSchemaValidator()

        valid_dataframe = polar_schema_validator.apply(
            dataframe=dataframe, schema=self._stock_instruments_valid_columns, ignore_columns=['id', 'sector', 'company_profile'])
        csv_file_name = (
            f"{datetime.now():%Y%m%d_%H%M%S}_"
            f"{uuid4().hex[:8]}.csv"
        )
        csv_file_path = Path(f"instrument_data/{csv_file_name}")
        complete_csv_file_path = DATA_DIR / csv_file_path
        valid_dataframe.write_csv(complete_csv_file_path)
        dataframe_columns = valid_dataframe.columns
        with self._unit_of_work as uow:
            result = uow.stock_instruments_repository.get_sync_report(
                csv_file_path=csv_file_path, valid_temp_table_columns=dataframe_columns)
            if result['update']:
                print("Update Records : ")
                polars_reader.read_dicts(result['update']).show_complete()
            else:
                print("Update Records : 0")

            if result['insert']:
                print("Insert Records : ")
                polars_reader.read_dicts(result['insert']).show_complete()
            else:
                print("Insert Records : 0")

            option = input("Make the insert update y/n : ")
            if option.__str__().lower() == 'y':
                result = uow.stock_instruments_repository.sync_report_with_existing_data(
                    csv_file_path=csv_file_path, valid_temp_table_columns=dataframe_columns)
                print(result)
            else:
                if option.__str__().lower() != 'n':
                    print("Invalid Option!")

        csv_file_path.unlink(missing_ok=True)

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
    def process_batch(
        self,
        batch
    ):

        print(
            f"Processing batch: {batch}"
            f"{len(batch)}"
        )
        with self._unit_of_work as uow:

            count = (
                uow.stock_instruments_repository.bulk_upsert(
                    batch
                )
            )

        print(
            f"Inserted/Updated: "
            f"{count}"
        )

    def get_instrument_details(self, trading_symbol=None, isin=None):

        filters = {}

        if trading_symbol:
            filters["trading_symbol"] = trading_symbol

        if isin:
            filters["isin"] = isin
        with self._unit_of_work as uow:

            result = uow.stock_instruments_repository.find_one(
                filters=filters
            )

        return result

    def get_company_instruments_stream(self, batch_size):
        with self._unit_of_work as uow:
            conditions = [
                uow.stock_instruments_repository._model.isin.isnot(None),
                uow.stock_instruments_repository._model.isin != ''
            ]
            instruments_stream = (
                uow.stock_instruments_repository
                .stream(
                    batch_size=batch_size,
                    conditions=conditions
                )
            )

        return instruments_stream

    def get_missing_companies_stream(self, batch_size: int | None = None):

        with self._unit_of_work as uow:
            stream = uow.company_profile_queries_repository.get_missing_companies_stream(
                batch_size=batch_size
            )

        return stream
