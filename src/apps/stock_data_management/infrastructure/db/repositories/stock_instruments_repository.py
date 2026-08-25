"""
Stock Instruments Repository Module.

Manages data access, staged bulk synchronization, diff reports, and queries
for NSE/BSE stock instruments in PostgreSQL.
"""

from typing import Any
from pathlib import Path
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData
from core.repositories.base_postgres_repository import BasePostgresRepository


class StockInstrumentsRepository(BasePostgresRepository[StockInstrumentsData]):
    """
    PostgreSQL repository for `StockInstrumentsData` records.

    Provides specialized routines for staging instruments into a temporary table,
    generating diff previews (insert vs update counts and before/after values),
    and performing batch synchronization.

    Attributes:
        _model (type[StockInstrumentsData]): Bound SQLAlchemy model class `StockInstrumentsData`.
    """

    _model = StockInstrumentsData

    def __init__(self, session: Session):
        """
        Initialize StockInstrumentsRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def _update_instrument_table_comparing_with_temp(self, valid_temp_table_columns: list[str]) -> int:
        """
        Execute an UPDATE on `stock_instruments_data` by joining with `tmp_stock_instruments_data`.

        Updates only rows where at least one matching column `IS DISTINCT FROM` the temp table value.

        Parameters:
            valid_temp_table_columns (list[str]): List of column names present in the temp staging table.

        Returns:
            int: Number of rows updated.

        Raises:
            Exception: If `valid_temp_table_columns` is empty.
        """
        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [
            k for k, v in self.get_valid_columns().items()
            if k in valid_temp_table_columns
        ]

        set_clause = ",\n".join(
            f"{c} = t.{c}"
            for c in valid_columns if c != 'instrument_key'
        )

        where_clause = "\nOR ".join(
            f"p.{c} IS DISTINCT FROM t.{c}"
            for c in valid_columns if c != 'instrument_key'
        )

        sql = f"""
            UPDATE {source_table} AS p
            SET {set_clause}
            FROM {temp_tablename} AS t 
            WHERE t.instrument_key = p.instrument_key AND ({where_clause});
        """
        res = self._session.execute(text(sql))
        return res.rowcount

    def _insert_into_instrument_table_comparing_with_temp(self, valid_temp_table_columns: list[str]) -> int:
        """
        Execute an INSERT into `stock_instruments_data` for records present in temp table but absent in main table.

        Parameters:
            valid_temp_table_columns (list[str]): List of column names in staging table.

        Returns:
            int: Number of rows inserted.

        Raises:
            Exception: If `valid_temp_table_columns` is empty.
        """
        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [
            k for k, v in self.get_valid_columns().items()
            if k in valid_temp_table_columns
        ]

        column_sql = ", ".join(f"{col}" for col in valid_columns)
        temp_table_column_sql = ", ".join(f"t.{col}" for col in valid_columns)

        sql = f"""
            INSERT INTO {source_table}
            ({column_sql})
            SELECT
            {temp_table_column_sql}
            FROM {temp_tablename} t
            LEFT JOIN {source_table} p
            ON p.instrument_key = t.instrument_key
            WHERE p.instrument_key IS NULL;
        """
        res = self._session.execute(text(sql))
        return res.rowcount

    def _get_expected_affecting_row_counts(self, valid_temp_table_columns: list[str]) -> dict[str, int]:
        """
        Count how many rows in staging table will result in new inserts vs updates.

        Parameters:
            valid_temp_table_columns (list[str]): Columns to compare.

        Returns:
            dict[str, int]: Dictionary containing:
                - 'insert': Count of new instruments to insert.
                - 'update': Count of existing instruments with changed attributes.

        Raises:
            Exception: If `valid_temp_table_columns` is empty.
        """
        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [
            k for k, v in self.get_valid_columns().items()
            if k in valid_temp_table_columns
        ]

        insert_sql = f"""
            SELECT
            COUNT(*) AS new_records
            FROM {temp_tablename} t
            LEFT JOIN {source_table} p
            ON p.instrument_key = t.instrument_key
            WHERE p.instrument_key IS NULL;
        """
        where_clause = "\nOR ".join(
            f"COALESCE(p.{c}, '') <> COALESCE(t.{c}, '')"
            for c in valid_columns
        )

        update_sql = f"""
            SELECT COUNT(*) expected_update_count FROM {source_table} p
            INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
            WHERE {where_clause}
        """

        return {
            "update": self._session.execute(text(update_sql)).scalar() or 0,
            "insert": self._session.execute(text(insert_sql)).scalar() or 0,
        }

    def _get_expected_affecting_rows(self, valid_temp_table_columns: list[str]) -> dict[str, list[dict[str, Any]]]:
        """
        Retrieve sample rows showing the before -> after diff for updates and full records for inserts.

        Parameters:
            valid_temp_table_columns (list[str]): Columns to compare.

        Returns:
            dict[str, list[dict[str, Any]]]: Mapping with 'update' list (with `old -> new` strings) and 'insert' list.

        Raises:
            Exception: If `valid_temp_table_columns` is empty.
        """
        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [
            k for k, v in self.get_valid_columns().items()
            if k in valid_temp_table_columns
        ]

        insert_column_sql = ", ".join(f"t.{col}" for col in valid_columns)

        insert_sql = f"""
            SELECT
            {insert_column_sql}
            FROM {temp_tablename} t
            LEFT JOIN {source_table} p
            ON p.instrument_key = t.instrument_key
            WHERE p.instrument_key IS NULL;
        """
        where_clause = "\nOR ".join(
            f"COALESCE(p.{c}, '') <> COALESCE(t.{c}, '')"
            for c in valid_columns
        )

        select_clause = ",\n".join(
            f"""
            CASE
                WHEN COALESCE(p.{column}, '') <> COALESCE(t.{column}, '')
                THEN CONCAT(
                    COALESCE(p.{column}, ''),
                    ' -> ',
                    COALESCE(t.{column}, '')
                )
                ELSE NULL
            END AS {column}
            """.strip()
            for column in valid_columns if column != 'instrument_key'
        )
        update_sql = f"""
            SELECT p.instrument_key, {select_clause} FROM {source_table} p
            INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
            WHERE {where_clause}
        """

        update_res = self._session.execute(text(update_sql)).mappings().all()
        insert_res = self._session.execute(text(insert_sql)).mappings().all()

        return {
            'update': update_res,
            'insert': insert_res
        }

    def get_sync_report(
        self,
        csv_file_path: str | Path,
        valid_temp_table_columns: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Create a staging table from a CSV file and generate a diff report of changes without committing modifications.

        Parameters:
            csv_file_path (str | Path): Path to staging CSV file.
            valid_temp_table_columns (list[str]): Columns to import into the temp table.

        Returns:
            dict[str, list[dict[str, Any]]]: Diff report with 'update' and 'insert' preview records.
        """
        self._create_temp_table_like()
        self._load_data_to_temp_table_from_csv(
            str(csv_file_path),
            valid_temp_table_columns
        )
        result = self._get_expected_affecting_rows(
            valid_temp_table_columns=valid_temp_table_columns
        )
        self._drop_temp_table()
        return result

    def sync_report_with_existing_data(
        self,
        csv_file_path: str | Path,
        valid_temp_table_columns: list[str]
    ) -> dict[str, int]:
        """
        Load CSV into staging table, execute bulk update on existing instruments, and insert new instruments.

        Parameters:
            csv_file_path (str | Path): Path to staging CSV.
            valid_temp_table_columns (list[str]): Column list matching the staging CSV layout.

        Returns:
            dict[str, int]: Counts dictionary with keys 'insert' and 'update'.
        """
        self._drop_temp_table()
        self._create_temp_table_like()
        print("Started Loading data into temporary table...", flush=True)
        self._load_data_to_temp_table_from_csv(
            str(csv_file_path),
            valid_temp_table_columns
        )

        print("Loading data into temporary table completed!!", flush=True)
        print("Started Updating Records...", flush=True)

        update_result = self._update_instrument_table_comparing_with_temp(
            valid_temp_table_columns=valid_temp_table_columns
        )
        print("Updating Records Completed!!", flush=True)
        print("Started Inserting Records...", flush=True)

        insert_result = self._insert_into_instrument_table_comparing_with_temp(
            valid_temp_table_columns=valid_temp_table_columns
        )
        print("Inserting Records Completed!!", flush=True)

        self._drop_temp_table()
        return {
            'insert': insert_result,
            'update': update_result
        }

    def fetch_instrument_keys_from_isin(self, isin: str) -> list[str]:
        """
        Fetch all instrument keys registered under an ISIN.

        Parameters:
            isin (str): 12-character International Securities Identification Number.

        Returns:
            list[str]: List of instrument keys matching the ISIN.
        """
        stmt = select(
            self._model.instrument_key
        ).where(
            self._model.isin == isin
        )

        result = self._session.scalars(statement=stmt).all()
        return list(result)
