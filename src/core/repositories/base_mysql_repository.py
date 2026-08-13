from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert

from core.models.base import MySQLBase
from sqlalchemy.orm import Session, sessionmaker


class BaseMySQLRepository:

    def __init__(
        self,
        model: MySQLBase,
        session: Session
    ):

        self.model = model
        self.tablename = model.__tablename__
        self.temp_tablename = f"tmp_{self.tablename}"

        self._session = (
            session
        )

    # ---------------------------------
    # INSERT ONE
    # ---------------------------------

    def insert_one(self, data):

        obj = self.model(**data)

        self._session.add(obj)

        self._session.refresh(obj)

        return obj

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records):

        if not records:
            return

        objects = [
            self.model(**record)
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
            self._session.query(self.model)
            .filter(
                self.model.id == record_id
            )
            .first()
        )

    # ---------------------------------
    # FIND ONE
    # ---------------------------------

    def find_one(self, filters):

        result = (
            self._session.query(self.model)
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
            self.model
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
            self._session.query(self.model)
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
            self._session.query(self.model)
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
        unique_columns=None
    ):

        if not records:
            return 0

        unique_columns = (
            unique_columns or []
        )

        stmt = insert(
            self.model
        ).values(records)

        update_dict = {

            c.name:
            stmt.inserted[c.name]

            for c in self.model.__table__.columns

            if c.name != "id"
            and c.name not in unique_columns
        }

        stmt = (
            stmt.on_duplicate_key_update(
                **update_dict
            )
        )

        result = self._session.execute(
            stmt
        )

        return result.rowcount

    # ---------------------------------
    #  STREAM LARGE DATASETS
    #  ---------------------------------
    def stream(self, filters=None, conditions=None, batch_size=1000):

        query = self._session.query(self.model)
        if filters:
            query = query.filter_by(**filters)
        if conditions:
            query = query.filter(*conditions)

        for row in query.yield_per(batch_size):
            yield row

    # ---------------------------------
    # UTILS
    # ---------------------------------

    def get_valid_columns(self):

        return {

            col.name: col.type

            for col
            in self.model.__table__.columns

            if col.name != "id"
        }

    def _create_temp_table_like(
        self,
        session,
        source_table: str | None = None,
    ):

        if not source_table:
            source_table = self.tablename
            temp_table = self.temp_tablename
        else:
            temp_table = f"tmp_{source_table}"
        sql = text(f"""
            CREATE TEMPORARY TABLE {temp_table}
            LIKE {source_table}
        """)

        self._session.execute(sql)

        return temp_table

    def _drop_temp_table(self, session, temp_tablename: str | None = None):

        if not temp_tablename:
            temp_tablename = self.temp_tablename

        sql = text(f"""
            DROP TEMPORARY TABLE IF EXISTS {temp_tablename}
        """)

        self._session.execute(sql)

    def _load_data_to_temp_table_from_csv(self, session, file_path, columns, temp_tablename: str | None = None) -> str:
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        column_sql = ", ".join(
            f"`{column}`"
            for column in columns
        )
        sql = f"""
                LOAD DATA LOCAL INFILE '{file_path}'
                INTO TABLE {temp_tablename}
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                IGNORE 1 ROWS
                ({column_sql});
            """
        self._session.execute(text(sql))

        return temp_tablename
