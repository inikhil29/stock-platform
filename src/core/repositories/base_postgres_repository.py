from sqlalchemy import func, inspect, text, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from typing import ClassVar, Generic, TypeVar

ModelT = TypeVar("ModelT")


class BasePostgresRepository(Generic[ModelT]):
    _model: ClassVar[type[ModelT]]

    def __init__(
        self,
        session: Session
    ):
        self.tablename = self._model.__tablename__
        self.temp_tablename = f"tmp_{self.tablename}"

        self._session = session

    # ---------------------------------
    # INSERT ONE
    # ---------------------------------

    def insert_one(self, data):

        obj = self._model(**data)

        self._session.add(obj)

        self._session.flush()

        return obj

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records):

        if not records:
            return

        objects = [
            self._model(**record)
            for record in records
        ]

        self._session.bulk_save_objects(
            objects
        )
    # ---------------------------------
    # FIND BY ID
    # ---------------------------------

    def find_by_id(self, record_id):

        return (
            self._session.query(self._model)
            .filter(
                self._model.id == record_id
            )
            .first()
        )

    # ---------------------------------
    # FIND ONE
    # ---------------------------------

    def find_one(self, filters):

        result = (
            self._session.query(self._model)
            .filter_by(**filters)
            .first()
        )

        return (
            result.to_dict()
            if result
            else None
        )

    # ---------------------------------
    # FIND MANY
    # ---------------------------------

    def find_many(
        self,
        filters=None,
        conditions=None,
        limit=100,
        offset=0
    ):

        query = self._session.query(
            self._model
        )

        if filters:

            query = query.filter_by(
                **filters
            )

        if conditions:

            query = query.filter(
                *conditions
            )

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    def update_one(
        self,
        filters,
        update_data
    ):

        count = (
            self._session.query(self._model)
            .filter_by(**filters)
            .update(update_data)
        )
        return count

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete_one(
        self,
        filters
    ):

        count = (
            self._session.query(self._model)
            .filter_by(**filters)
            .delete()
        )
        return count

    # ---------------------------------
    # BULK UPSERT
    # ---------------------------------

    def bulk_upsert(
        self,
        records,
        unique_columns=None,
        update_dict=None
    ):
        if not records:
            return

        unique_columns = unique_columns or []

        stmt = insert(self._model).values(records)

        primary_key_columns = {
            column.name
            for column in inspect(self._model).primary_key
        }

        if not update_dict:

            update_dict = {
                c.name: stmt.excluded[c.name]
                for c in self._model.__table__.columns
                if c.name not in primary_key_columns
                and c.name not in unique_columns
            }
        if not unique_columns:
            unique_columns = [i for i in update_dict]

        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_dict
        )

        result = self._session.execute(stmt)
        return result.rowcount

    def upsert(
        self,
        record,
        unique_columns=None
    ):
        if not record:
            return

        unique_columns = unique_columns or []

        stmt = insert(self._model).values(record)

        primary_key_columns = [
            column.name for column in inspect(self._model).primary_key]

        update_dict = {
            c.name: stmt.excluded[c.name]
            for c in self._model.__table__.columns
            if c.name not in primary_key_columns
            and c.name not in unique_columns
        }
        if not unique_columns:
            unique_columns = [i for i in update_dict]

        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_dict
        )

        result = self._session.execute(stmt)
        return result.rowcount

    # ---------------------------------
    #  STREAM LARGE DATASETS
    #  ---------------------------------
    def stream(self, filters=None, conditions=None, batch_size=1000):
        stmt = select(self._model)
        if filters:
            stmt = stmt.filter_by(**filters)

        if conditions:
            stmt = stmt.where(*conditions)

        result = self._session.scalars(
            stmt.execution_options(yield_per=batch_size)
        )

        for row in result:
            yield row

    # ---------------------------------
    # UTILS
    # ---------------------------------

    def get_valid_columns(self):

        return {

            col.name: col.type
            for col
            in self._model.__table__.columns
        }

    def _create_temp_table_like(
        self,
        source_table: str | None = None,
    ):

        if not source_table:
            source_table = self.tablename
            temp_table = self.temp_tablename
        else:
            temp_table = f"tmp_{source_table}"
        sql = text(f"""
            CREATE TEMPORARY TABLE IF NOT EXISTS {temp_table}(
                LIKE {source_table}
                INCLUDING ALL
            )
            """
                   )

        self._session.execute(sql)
        return temp_table

    def _drop_temp_table(self, temp_tablename: str | None = None):

        if not temp_tablename:
            temp_tablename = self.temp_tablename

        sql = text(f"""
            DROP TABLE IF EXISTS {temp_tablename}
        """)

        self._session.execute(sql)

    def _load_data_to_temp_table_from_csv(self, file_path, columns, temp_tablename: str | None = None) -> str:
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        column_sql = ", ".join(
            f"{column}"
            for column in columns
        )
        sql = f"""
                COPY {temp_tablename}
                ({column_sql})
                FROM '/tmp/{file_path}'
                WITH (
                    FORMAT csv,
                    HEADER true,
                    DELIMITER ',',
                    QUOTE '"'
                );
                """
        self._session.execute(text(sql))

        return temp_tablename

    def _upsert_and_get_id(self, insert_data: dict, update_data: dict, unique_columns: list) -> int:
        stmt = insert(self._model).values(
            insert_data
        )
        primary_key = inspect(self._model).primary_key[0]
        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_data
        ).returning(primary_key)

        return self._session.scalar(stmt)
