from sqlalchemy import text
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData
from core.repositories.base_postgres_repository import BasePostgresRepository


class StockInstrumentsRepository(
    BasePostgresRepository[StockInstrumentsData]
):
    _model = StockInstrumentsData

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def _update_instrument_table_comparing_with_temp(self, valid_temp_table_columns: list[str]) -> str:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        set_clause = ",\n".join(
            f"{c} = t.{c}"
            for c in valid_columns if c != 'instrument_key'
        )

        where_clause = "\nOR ".join(
            f"p.{c} IS DISTINCT FROM t.{c}"
            for c in valid_columns if c != 'instrument_key'
        )

        sql = f""" UPDATE {source_table} AS p
            SET {set_clause}
            FROM {temp_tablename} AS t 
            WHERE t.instrument_key = p.instrument_key AND ({where_clause});
            """
        res = self._session.execute(text(sql))
        return res.rowcount

    def _insert_into_instrument_table_comparing_with_temp(self, valid_temp_table_columns: list[str]) -> str:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        coloumn_sql = ", ".join(
            [f"{col}" for col in valid_columns]
        )
        temp_table_coloumn_sql = ", ".join(
            [f"t.{col}" for col in valid_columns]
        )

        sql = f"""
                INSERT INTO {source_table}
                ({coloumn_sql})
                SELECT
                {temp_table_coloumn_sql}
                FROM {temp_tablename} t
                LEFT JOIN {source_table} p
                ON p.instrument_key = t.instrument_key
                WHERE p.instrument_key IS NULL;
            """
        res = self._session.execute(text(sql))
        return res.rowcount

    def _get_expected_affecting_row_counts(self, valid_temp_table_columns: list[str]) -> dict:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        insert_sql = f"""
                    SELECT
                    COUNT(*) AS new_records
                    FROM {temp_tablename} t
                    LEFT JOIN {source_table} p
                    ON p.instrument_key = t.instrument_key
                    WHERE p.instrument_key IS NULL;
                """
        where_clause = "\nOR ".join(
            f"COALESCE(p.{c}, '')  COALESCE(t.{c}, '')"
            for c in valid_columns
        )

        update_sql = f""" SELECT COUNT(*) expected_update_count FROM {source_table} p
                    INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
                    WHERE {where_clause}
            """

        return {
            "update": self._session.execute(text(update_sql)).scalar(),
            "insert": self._session.execute(text(insert_sql)).scalar(),
        }

    def _get_expected_affecting_rows(self, valid_temp_table_columns: list[str]) -> dict:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        coloumn_sql = ", ".join(
            [f"t.{col}" for col in valid_columns]
        )

        insert_sql = f"""
                        SELECT
                        {coloumn_sql}
                        FROM {temp_tablename} t
                        LEFT JOIN {source_table} p
                        ON p.instrument_key = t.instrument_key
                        WHERE p.instrument_key IS NULL;
                    """
        where_clause = "\nOR ".join(
            f"COALESCE(p.{c}, '') <> COALESCE(t.{c}, '')"
            for c in valid_columns
        )

        coloumn_sql = ", ".join(
            [f"p.{col}" for col in valid_columns]
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
        update_sql = f""" SELECT p.instrument_key, {select_clause} FROM {source_table} p
                        INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
                        WHERE {where_clause}
                """

        update_res = self._session.execute(text(update_sql)).mappings().all()

        insert_res = self._session.execute(text(insert_sql)).mappings().all()

        return {
            'update':  update_res,
            'insert': insert_res
        }

    def get_sync_report(self, csv_file_path, valid_temp_table_columns):

        self._create_temp_table_like()
        self._load_data_to_temp_table_from_csv(
            csv_file_path,
            valid_temp_table_columns
        )
        result = self._get_expected_affecting_rows(
            valid_temp_table_columns=valid_temp_table_columns
        )
        self._drop_temp_table()
        return result

    def sync_report_with_existing_data(self, csv_file_path, valid_temp_table_columns):

        self._drop_temp_table()
        self._create_temp_table_like()
        print("Started Loading data into temporary table...", flush=True)
        self._load_data_to_temp_table_from_csv(
            csv_file_path,
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
