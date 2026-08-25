"""
Stock Instruments Service Module.

Responsible for extracting, validating, transforming, and synchronizing
NSE/BSE financial instrument metadata into PostgreSQL.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from uuid import uuid4

import ijson
import pandas as pd

from apps.stock_data_management.infrastructure.clients.stock_instruments_client import StockInstrumentsClient
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from core.config.paths import DATA_DIR
from core.dataframe.engines.polars.reader import PolarsReader
from core.dataframe.engines.polars.schema_validator import PolarsSchemaValidator

logger = logging.getLogger(__name__)


class StockInstrumentsService:
    """
    Service layer for managing financial instrument records (stocks, indices, derivatives).

    Provides functionality for streaming and batch synchronization of Upstox instrument files,
    database lookups by trading symbol or ISIN, and streaming generators for ETL pipelines.

    Attributes:
        _unit_of_work (PostgresUnitOfWork): Unit of Work coordinating database transactions and repositories.
        _stock_instruments_valid_columns (dict): Mapping of column names to SQL types for the instruments table.
        _stock_instrument_client (StockInstrumentsClient): API client for fetching instrument metadata.
    """

    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_instrument_client: StockInstrumentsClient
    ):
        """
        Initialize the StockInstrumentsService.

        Parameters:
            unit_of_work (PostgresUnitOfWork): Database Unit of Work instance for repository management.
            stock_instrument_client (StockInstrumentsClient): HTTP client communicating with Upstox API.
        """
        self._unit_of_work = unit_of_work
        with self._unit_of_work as uow:
            self._stock_instruments_valid_columns = uow.stock_instruments_repository.get_valid_columns()

        self._stock_instrument_client = stock_instrument_client

    # ---------------------------------
    # PROCESS FILE
    # ---------------------------------

    def sync_instruments(
        self,
        json_file_path: str | Path,
        batch_size: int = 1000
    ) -> None:
        """
        Stream, transform, and bulk-upsert instrument records from a JSON file into PostgreSQL.

        Uses `ijson` for iterative memory-efficient JSON parsing, transforming records into
        the target schema and inserting them in batches.

        Parameters:
            json_file_path (str | Path): Absolute or relative path to the uncompressed JSON file.
            batch_size (int, optional): Number of records to accumulate before bulk upserting. Defaults to 1000.

        Raises:
            Exception: If unrecoverable errors occur during file parsing or database insertion.
        """
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
                            row=row,
                            valid_columns=self._stock_instruments_valid_columns
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
                    logger.exception("Error processing row %d: %s", row_number, e)
                    raise

            if batch:
                self.process_batch(batch)
                batch.clear()

    def sync_instruments_new(self, json_file_path: str | Path) -> None:
        """
        Synchronize instruments using the Polars DataFrame engine and PostgreSQL temporary staging table.

        Reads the JSON file into a Polars DataFrame, validates and casts columns against the
        target table schema, exports to a staging CSV, loads into a temporary table, prints
        an interactive diff report (inserts vs updates), and conditionally executes the sync.

        Parameters:
            json_file_path (str | Path): Path to the uncompressed JSON instrument file.
        """
        polars_reader = PolarsReader()
        dataframe = polars_reader.read_json(
            json_file_path, infer_schema_length=None)

        polar_schema_validator = PolarsSchemaValidator()

        valid_dataframe = polar_schema_validator.apply(
            dataframe=dataframe, schema=self._stock_instruments_valid_columns, ignore_columns=['id', 'sector', 'company_profile', 'created_at', 'updated_at'])
        csv_file_name = (
            f"{datetime.now():%Y%m%d_%H%M%S}_"
            f"{uuid4().hex[:8]}.csv"
        )
        csv_file_path = Path(f"instrument_data/{csv_file_name}")
        complete_csv_file_path = DATA_DIR / csv_file_path
        valid_dataframe.write_csv(str(complete_csv_file_path))
        dataframe_columns = valid_dataframe.columns
        try:
            with self._unit_of_work as uow:
                result = uow.stock_instruments_repository.get_sync_report(
                    csv_file_path=csv_file_path, valid_temp_table_columns=dataframe_columns)
            if result['update']:
                print("Update Records : ")
                polars_reader.read_dicts(
                    result['update'], infer_schema_length=None).show_complete()
            else:
                print("Update Records : 0")

            if result['insert']:
                print("Insert Records : ")
                polars_reader.read_dicts(
                    result['insert'], infer_schema_length=None).show_complete()
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
        finally:
            complete_csv_file_path.unlink(missing_ok=True)

    # ---------------------------------
    # TRANSFORM RECORD
    # ---------------------------------

    def _transform_record(
        self,
        row: dict[str, Any],
        valid_columns: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Filter and normalize a single raw instrument dictionary against valid table columns.

        Reindexes the row keys to match table schema and replaces NaN/null values with None.

        Parameters:
            row (dict[str, Any]): Raw JSON item parsed from the instrument file.
            valid_columns (dict[str, Any]): Schema dictionary representing valid table columns.

        Returns:
            dict[str, Any] | None: Normalized column-to-value dictionary, or None if row is empty.
        """

        filtered = {

            k: v

            for k, v in row.items()

            if k in valid_columns
        }

        if not filtered:
            return None

        filtered_series = (
            pd.Series(filtered)
            .astype(object)
            .reindex(list(valid_columns.keys()))
        )

        filtered_series = filtered_series.where(
            pd.notnull(filtered_series),
            None
        )

        return filtered_series.to_dict()

    # ---------------------------------
    # PROCESS BATCH
    # ---------------------------------
    def process_batch(
        self,
        batch: list[dict[str, Any]]
    ) -> None:
        """
        Execute a bulk upsert of instrument records within a Unit of Work transaction.

        Parameters:
            batch (list[dict[str, Any]]): List of normalized instrument dictionaries to upsert.
        """

        print(
            f"Processing batch: {len(batch)} records"
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

    def get_instrument_details(
        self,
        trading_symbol: str | None = None,
        isin: str | None = None
    ) -> dict[str, Any] | None:
        """
        Query database for a single instrument matching the given trading symbol or ISIN.

        Parameters:
            trading_symbol (str | None, optional): Trading symbol (e.g. 'RELIANCE', 'TCS'). Defaults to None.
            isin (str | None, optional): 12-character International Securities Identification Number. Defaults to None.

        Returns:
            dict[str, Any] | None: Instrument details dictionary if found, None otherwise.
        """

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

    def get_company_instruments_stream(
        self,
        batch_size: int = 1000
    ) -> Generator[StockInstrumentsData, None, None]:
        """
        Stream instrument records from the database that have a non-empty ISIN.

        Yields records one by one while keeping the Unit of Work database session open.

        Parameters:
            batch_size (int, optional): Number of rows fetched per batch cursor. Defaults to 1000.

        Yields:
            StockInstrumentsData: ORM model instance for each company instrument.
        """
        with self._unit_of_work as uow:
            conditions = [
                uow.stock_instruments_repository._model.isin.isnot(None),
                uow.stock_instruments_repository._model.isin != ''
            ]
            yield from uow.stock_instruments_repository.stream(
                batch_size=batch_size,
                conditions=conditions
            )

    def get_missing_companies_stream(
        self,
        batch_size: int | None = 1000
    ) -> Generator[StockInstrumentsData, None, None]:
        """
        Stream company instruments that exist in stock_instruments_data but lack a company profile record.

        Yields records one by one within an active Unit of Work context.

        Parameters:
            batch_size (int | None, optional): Number of rows fetched per batch cursor. Defaults to 1000.

        Yields:
            StockInstrumentsData: Instrument model instance missing profile information.
        """

        with self._unit_of_work as uow:
            yield from uow.company_profile_queries_repository.get_missing_companies_stream(
                batch_size=batch_size
            )

    def fetch_instrument_keys_from_isin(self, isin: str) -> list[str]:
        """
        Retrieve all instrument keys associated with a given ISIN (e.g. across NSE and BSE).

        Parameters:
            isin (str): 12-character International Securities Identification Number.

        Returns:
            list[str]: List of instrument keys (e.g. ['NSE_EQ|INE002A01018', 'BSE_EQ|INE002A01018']).
        """
        with self._unit_of_work as uow:
            return uow.stock_instruments_repository.fetch_instrument_keys_from_isin(isin=isin)
