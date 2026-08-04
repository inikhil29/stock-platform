from sqlalchemy import text
from core.repositories.base_mysql_repository import BaseMySQLRepository


class UpstoxInstrumentRepository(
    BaseMySQLRepository
):

    def __init__(self, session_factory, model):

        super().__init__(
            model=model,
            session_factory=session_factory
        )

    def _update_instrument_table_comparing_with_temp(self, session, valid_temp_table_columns: list[str]) -> str:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        set_clause = ",\n".join(
            f"p.`{c}` = t.`{c}`"
            for c in valid_columns if c != 'instrument_key'
        )

        where_clause = "\nOR ".join(
            f"IFNULL(p.`{c}`, '') <> IFNULL(t.`{c}`, '')"
            for c in valid_columns if c != 'instrument_key'
        )

        sql = f""" UPDATE {source_table} p
            INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
            SET {set_clause}
            WHERE {where_clause};
            """

        res = session.execute(text(sql))
        session.commit()
        return res.rowcount

    def _insert_into_instrument_table_comparing_with_temp(self, session, valid_temp_table_columns: list[str]) -> str:

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
        res = session.execute(text(sql))
        session.commit()
        return res.rowcount

    def _get_expected_affecting_row_counts(self, session, valid_temp_table_columns: list[str]) -> dict:

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
            f"IFNULL(p.`{c}`, '') <> IFNULL(t.`{c}`, '')"
            for c in valid_columns
        )

        update_sql = f""" SELECT COUNT(*) expected_update_count FROM {source_table} p
                    INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
                    WHERE {where_clause}
            """

        return {
            "update": session.execute(text(update_sql)).scalar(),
            "insert": session.execute(text(insert_sql)).scalar(),
        }

    def _get_expected_affecting_rows(self, session, valid_temp_table_columns: list[str]) -> dict:

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
            f"IFNULL(p.`{c}`, '') <> IFNULL(t.`{c}`, '')"
            for c in valid_columns
        )

        coloumn_sql = ", ".join(
            [f"p.{col}" for col in valid_columns]
        )

        select_clause = ",\n".join(
            f"""
            CASE
                WHEN IFNULL(p.`{column}`, '') <> IFNULL(t.`{column}`, '')
                THEN CONCAT(
                    IFNULL(p.`{column}`, ''),
                    ' -> ',
                    IFNULL(t.`{column}`, '')
                )
                ELSE NULL
            END AS `{column}`
            """.strip()
            for column in valid_columns if column != 'instrument_key'
        )
        update_sql = f""" SELECT p.instrument_key, {select_clause} FROM {source_table} p
                        INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key
                        WHERE {where_clause}
                """

        update_res = session.execute(text(update_sql)).mappings().all()

        insert_res = session.execute(text(insert_sql)).mappings().all()

        return {
            'update':  update_res,
            'insert': insert_res
        }

    def get_sync_report(self, csv_file_path, valid_temp_table_columns):
        with self.session_factory() as session:
            self._create_temp_table_like(session)
            self._load_data_to_temp_table_from_csv(
                session, csv_file_path, valid_temp_table_columns)
            result = self._get_expected_affecting_rows(
                session=session, valid_temp_table_columns=valid_temp_table_columns)
            self._drop_temp_table(session=session)
            return result

    def sync_report_with_existing_data(self, csv_file_path, valid_temp_table_columns):
        with self.session_factory() as session:
            self._drop_temp_table(session=session)
            self._create_temp_table_like(session)
            self._load_data_to_temp_table_from_csv(
                session, csv_file_path, valid_temp_table_columns)
            update_result = self._update_instrument_table_comparing_with_temp(
                session=session, valid_temp_table_columns=valid_temp_table_columns)
            insert_result = self._insert_into_instrument_table_comparing_with_temp(
                session=session, valid_temp_table_columns=valid_temp_table_columns)

            self._drop_temp_table(session=session)
            return {
                'insert': insert_result,
                'update': update_result
            }
