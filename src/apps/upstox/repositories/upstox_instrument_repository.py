from sqlalchemy import text
from core.repositories.base_mysql_repository import BaseMySQLRepository


class UpstoxInstrumentRepository(
    BaseMySQLRepository
):

    def __init__(self, model, session_factory):

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
            for c in valid_columns
        )

        where_clause = "\nOR ".join(
            f"IFNULL(p.`{c}`, '') <> IFNULL(t.`{c}`, '')"
            for c in valid_columns
        )

        sql = f""" UPDATE {source_table} p 
            INNER JOIN {temp_tablename} t ON t.instrument_key = p.instrument_key 
            SET {set_clause}
            WHERE {where_clause}; 
            """

        session.execute(text(sql))
        session.commit()

    def _update_instrument_table_comparing_with_temp(self, session, valid_temp_table_columns: list[str]) -> str:

        if not valid_temp_table_columns:
            raise Exception("No valid column list is provided.")
        source_table = self.tablename
        temp_tablename = self.temp_tablename
        valid_columns = [k for k, v in self.get_valid_columns(
        ).items() if k in valid_temp_table_columns]

        sql = f"""
                INSERT INTO {source_table}
                ({valid_columns})
                SELECT
                {valid_columns}
                FROM {temp_tablename} t
                LEFT JOIN {source_table} p
                ON p.instrument_key = t.instrument_key
                WHERE p.instrument_key IS NULL;
            """
        session.execute(text(sql))
        session.commit()

    def _get_expected_affecting_row_counts(self, session, valid_temp_table_columns: list[str]) -> str:

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

    def get_sync_report(self, csv_file_path, valid_temp_table_columns):
        with self.session_factory() as session:
            self._create_temp_table_like(session)
            self._load_data_to_temp_table_from_csv(session, csv_file_path, valid_temp_table_columns)
            result = self._get_expected_affecting_row_counts(session=session, valid_temp_table_columns=valid_temp_table_columns)
            self._drop_temp_table(session=session)
            return result
