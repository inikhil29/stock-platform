"""
Base PostgreSQL Repository Module.

Provides a generic repository pattern implementation for PostgreSQL database operations
using SQLAlchemy, including single-record CRUD, bulk upserting, temp staging tables, and cursor streaming.
"""

from typing import Any, ClassVar, Generator, Generic, TypeVar
from sqlalchemy import func, inspect, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BasePostgresRepository(Generic[ModelT]):
    """
    Generic base repository providing data access and manipulation methods for PostgreSQL ORM models.

    Attributes:
        _model (ClassVar[type[ModelT]]): SQLAlchemy model class bound to this repository.
        tablename (str): Name of the underlying database table.
        temp_tablename (str): Name of temporary staging table (`tmp_<tablename>`).
        _session (Session): Active SQLAlchemy database session.
    """

    _model: ClassVar[type[ModelT]]

    def __init__(self, session: Session):
        """
        Initialize the repository with an active SQLAlchemy database session.

        Parameters:
            session (Session): SQLAlchemy ORM session bound to a transaction.
        """
        self.tablename = self._model.__tablename__
        self.temp_tablename = f"tmp_{self.tablename}"
        self._session = session

    # ---------------------------------
    # INSERT ONE
    # ---------------------------------

    def insert_one(self, data: dict[str, Any]) -> ModelT:
        """
        Insert a single entity record into the database and flush the session.

        Parameters:
            data (dict[str, Any]): Dictionary of column-value pairs representing the record.

        Returns:
            ModelT: The persisted SQLAlchemy ORM instance with populated IDs/defaults.
        """
        obj = self._model(**data)
        self._session.add(obj)
        self._session.flush()
        return obj

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records: list[dict[str, Any]]) -> None:
        """
        Bulk insert multiple entity records into the database.

        Parameters:
            records (list[dict[str, Any]]): List of row dictionaries to persist.
        """
        if not records:
            return

        objects = [
            self._model(**record)
            for record in records
        ]
        self._session.bulk_save_objects(objects)

    # ---------------------------------
    # FIND BY ID
    # ---------------------------------

    def find_by_id(self, record_id: int | str) -> ModelT | None:
        """
        Find a single record by its primary key ID.

        Parameters:
            record_id (int | str): Primary key value.

        Returns:
            ModelT | None: The matching ORM model instance if found, None otherwise.
        """
        return (
            self._session.query(self._model)
            .filter(self._model.id == record_id)
            .first()
        )

    # ---------------------------------
    # FIND ONE
    # ---------------------------------

    def find_one(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        """
        Find the first record matching exact column-value filters and return it as a dictionary.

        Parameters:
            filters (dict[str, Any]): Column-value dictionary for equality filtering.

        Returns:
            dict[str, Any] | None: Model converted to dictionary if found, None otherwise.
        """
        result = (
            self._session.query(self._model)
            .filter_by(**filters)
            .first()
        )
        return result.to_dict() if result else None

    # ---------------------------------
    # FIND MANY
    # ---------------------------------

    def find_many(
        self,
        filters: dict[str, Any] | None = None,
        conditions: list[Any] | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[ModelT]:
        """
        Find multiple records with optional filters, conditions, pagination limits, and offsets.

        Parameters:
            filters (dict[str, Any] | None, optional): Keyword filters applied via `filter_by`. Defaults to None.
            conditions (list[Any] | None, optional): SQLAlchemy BinaryExpressions applied via `filter`. Defaults to None.
            limit (int, optional): Maximum number of rows to retrieve. Defaults to 100.
            offset (int, optional): Number of rows to skip. Defaults to 0.

        Returns:
            list[ModelT]: List of matched ORM model instances.
        """
        query = self._session.query(self._model)

        if filters:
            query = query.filter_by(**filters)

        if conditions:
            query = query.filter(*conditions)

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
        filters: dict[str, Any],
        update_data: dict[str, Any]
    ) -> int:
        """
        Update matching records in-place with the specified values.

        Parameters:
            filters (dict[str, Any]): Equality filter criteria for records to update.
            update_data (dict[str, Any]): Column-value pairs to set.

        Returns:
            int: Number of rows affected by the update.
        """
        count = (
            self._session.query(self._model)
            .filter_by(**filters)
            .update(update_data)
        )
        return count

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete_one(self, filters: dict[str, Any]) -> int:
        """
        Delete records matching the specified equality filter criteria.

        Parameters:
            filters (dict[str, Any]): Filter dictionary specifying records to delete.

        Returns:
            int: Number of deleted rows.
        """
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
        records: list[dict[str, Any]],
        unique_columns: list[str] | None = None,
        update_dict: dict[str, Any] | None = None
    ) -> int:
        """
        Bulk upsert multiple records using PostgreSQL `ON CONFLICT DO UPDATE`.

        Parameters:
            records (list[dict[str, Any]]): List of row dictionaries to insert/update.
            unique_columns (list[str] | None, optional): Unique constraint column names forming the conflict target. Defaults to None.
            update_dict (dict[str, Any] | None, optional): Custom column-value mapping for update clause. Defaults to all non-PK columns.

        Returns:
            int: Total number of rows inserted or updated.
        """
        if not records:
            return 0

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
            unique_columns = list(update_dict.keys())

        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_dict
        )

        result = self._session.execute(stmt)
        return result.rowcount

    def upsert(
        self,
        record: dict[str, Any],
        unique_columns: list[str] | None = None
    ) -> int:
        """
        Upsert a single record using PostgreSQL `ON CONFLICT DO UPDATE`.

        Parameters:
            record (dict[str, Any]): Row dictionary to insert or update on conflict.
            unique_columns (list[str] | None, optional): Column names defining unique constraint. Defaults to None.

        Returns:
            int: Number of rows affected (1 for insert/update, 0 if unchanged).
        """
        if not record:
            return 0

        unique_columns = unique_columns or []
        stmt = insert(self._model).values(record)

        primary_key_columns = [
            column.name for column in inspect(self._model).primary_key
        ]

        update_dict = {
            c.name: stmt.excluded[c.name]
            for c in self._model.__table__.columns
            if c.name not in primary_key_columns
            and c.name not in unique_columns
        }
        if not unique_columns:
            unique_columns = list(update_dict.keys())

        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_dict
        )

        result = self._session.execute(stmt)
        return result.rowcount

    # ---------------------------------
    # STREAM LARGE DATASETS
    # ---------------------------------

    def stream(
        self,
        filters: dict[str, Any] | None = None,
        conditions: list[Any] | None = None,
        batch_size: int = 1000
    ) -> Generator[ModelT, None, None]:
        """
        Stream large datasets efficiently using server-side cursor batching (`yield_per`).

        Parameters:
            filters (dict[str, Any] | None, optional): Keyword filters applied via `filter_by`. Defaults to None.
            conditions (list[Any] | None, optional): SQL expressions applied via `where`. Defaults to None.
            batch_size (int, optional): Number of rows fetched per batch cursor chunk. Defaults to 1000.

        Yields:
            ModelT: Individual ORM model instances.
        """
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

    def get_valid_columns(self) -> dict[str, Any]:
        """
        Get a mapping of table column names to their SQLAlchemy column types.

        Returns:
            dict[str, Any]: Dictionary mapping column names to SQLAlchemy data types.
        """
        return {
            col.name: col.type
            for col in self._model.__table__.columns
        }

    def _create_temp_table_like(
        self,
        source_table: str | None = None,
    ) -> str:
        """
        Create a PostgreSQL temporary table matching the schema of a target table.

        Parameters:
            source_table (str | None, optional): Source table name to clone structure from. Defaults to model's table name.

        Returns:
            str: The name of the temporary table created.
        """
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
        """)
        self._session.execute(sql)
        return temp_table

    def _drop_temp_table(self, temp_tablename: str | None = None) -> None:
        """
        Drop temporary staging table if it exists.

        Parameters:
            temp_tablename (str | None, optional): Name of temporary table to drop. Defaults to self.temp_tablename.
        """
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        sql = text(f"""
            DROP TABLE IF EXISTS {temp_tablename}
        """)
        self._session.execute(sql)

    def _load_data_to_temp_table_from_csv(
        self,
        file_path: str,
        columns: list[str],
        temp_tablename: str | None = None
    ) -> str:
        """
        Load CSV data into temporary table using PostgreSQL `COPY FROM`.

        Parameters:
            file_path (str): Relative path to CSV inside data directory.
            columns (list[str]): List of column names matching CSV header layout.
            temp_tablename (str | None, optional): Target staging table name. Defaults to self.temp_tablename.

        Returns:
            str: Target temporary table name populated with CSV records.
        """
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        column_sql = ", ".join(f"{column}" for column in columns)
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

    def _upsert_and_get_id(
        self,
        insert_data: dict[str, Any],
        update_data: dict[str, Any],
        unique_columns: list[Any]
    ) -> int:
        """
        Upsert a record and return its primary key ID using `RETURNING id`.

        Parameters:
            insert_data (dict[str, Any]): Dictionary of values to insert.
            update_data (dict[str, Any]): Dictionary of column-to-value assignments for conflict resolution.
            unique_columns (list[Any]): List of Column elements or column names forming unique constraint index.

        Returns:
            int: Primary key ID of the inserted or updated record.
        """
        stmt = insert(self._model).values(insert_data)
        primary_key = inspect(self._model).primary_key[0]
        stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=update_data
        ).returning(primary_key)

        return self._session.scalar(stmt)
