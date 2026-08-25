"""
Base MySQL Repository Module.

Provides a generic repository pattern implementation for MySQL database operations
using SQLAlchemy, including single-record CRUD, bulk upsert via `ON DUPLICATE KEY UPDATE`,
temporary tables, and cursor streaming.
"""

from typing import Any, Generator
from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from core.models.base import MySQLBase


class BaseMySQLRepository:
    """
    Generic base repository providing data access and manipulation methods for MySQL ORM models.

    Attributes:
        model (type[MySQLBase]): SQLAlchemy MySQL model class bound to this repository.
        tablename (str): Name of the database table.
        temp_tablename (str): Name of temporary staging table (`tmp_<tablename>`).
        _session (Session): Active SQLAlchemy database session.
    """

    def __init__(
        self,
        model: type[MySQLBase],
        session: Session
    ):
        """
        Initialize BaseMySQLRepository.

        Parameters:
            model (type[MySQLBase]): MySQLBase model class.
            session (Session): Active SQLAlchemy database session.
        """
        self.model = model
        self.tablename = model.__tablename__
        self.temp_tablename = f"tmp_{self.tablename}"
        self._session = session

    # ---------------------------------
    # INSERT ONE
    # ---------------------------------

    def insert_one(self, data: dict[str, Any]) -> Any:
        """
        Insert a single entity record and refresh instance attributes.

        Parameters:
            data (dict[str, Any]): Dictionary of column-value pairs representing the record.

        Returns:
            Any: Persisted ORM model instance.
        """
        obj = self.model(**data)
        self._session.add(obj)
        self._session.refresh(obj)
        return obj

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records: list[dict[str, Any]]) -> None:
        """
        Bulk insert multiple records into the database.

        Parameters:
            records (list[dict[str, Any]]): List of row dictionaries.
        """
        if not records:
            return

        objects = [
            self.model(**record)
            for record in records
        ]
        self._session.bulk_save_objects(objects)

    # ---------------------------------
    # FIND BY ID
    # ---------------------------------

    def find_by_id(self, record_id: int | str) -> Any | None:
        """
        Find a single record by primary key ID.

        Parameters:
            record_id (int | str): Primary key value.

        Returns:
            Any | None: Matching model instance if found, None otherwise.
        """
        return (
            self._session.query(self.model)
            .filter(self.model.id == record_id)
            .first()
        )

    # ---------------------------------
    # FIND ONE
    # ---------------------------------

    def find_one(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        """
        Find first record matching filters and return it as a dictionary.

        Parameters:
            filters (dict[str, Any]): Equality filter criteria.

        Returns:
            dict[str, Any] | None: Model dictionary if found, None otherwise.
        """
        result = (
            self._session.query(self.model)
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
    ) -> list[Any]:
        """
        Find multiple records with optional filters, conditions, limit, and offset.

        Parameters:
            filters (dict[str, Any] | None, optional): Exact match filters. Defaults to None.
            conditions (list[Any] | None, optional): Binary filter expressions. Defaults to None.
            limit (int, optional): Maximum rows to return. Defaults to 100.
            offset (int, optional): Rows to skip. Defaults to 0.

        Returns:
            list[Any]: List of matching ORM models.
        """
        query = self._session.query(self.model)

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
        Update records matching filter criteria with new data.

        Parameters:
            filters (dict[str, Any]): Filter specifying records to update.
            update_data (dict[str, Any]): New column values to apply.

        Returns:
            int: Number of updated rows.
        """
        count = (
            self._session.query(self.model)
            .filter_by(**filters)
            .update(update_data)
        )
        return count

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete_one(self, filters: dict[str, Any]) -> int:
        """
        Delete records matching filter criteria.

        Parameters:
            filters (dict[str, Any]): Filter criteria.

        Returns:
            int: Number of deleted rows.
        """
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
        records: list[dict[str, Any]],
        unique_columns: list[str] | None = None
    ) -> int:
        """
        Bulk upsert multiple records using MySQL `ON DUPLICATE KEY UPDATE`.

        Parameters:
            records (list[dict[str, Any]]): List of row dictionaries.
            unique_columns (list[str] | None, optional): Unique columns excluded from the update dict. Defaults to None.

        Returns:
            int: Number of rows inserted or updated.
        """
        if not records:
            return 0

        unique_columns = unique_columns or []
        stmt = insert(self.model).values(records)

        update_dict = {
            c.name: stmt.inserted[c.name]
            for c in self.model.__table__.columns
            if c.name != "id"
            and c.name not in unique_columns
        }

        stmt = stmt.on_duplicate_key_update(**update_dict)
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
    ) -> Generator[Any, None, None]:
        """
        Stream large datasets efficiently using server-side cursor batching.

        Parameters:
            filters (dict[str, Any] | None, optional): Equality filters. Defaults to None.
            conditions (list[Any] | None, optional): Binary filter expressions. Defaults to None.
            batch_size (int, optional): Batch size. Defaults to 1000.

        Yields:
            Any: Individual ORM model instances.
        """
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

    def get_valid_columns(self) -> dict[str, Any]:
        """
        Get a mapping of table column names to their SQLAlchemy types (excluding 'id').

        Returns:
            dict[str, Any]: Dictionary mapping column names to SQLAlchemy types.
        """
        return {
            col.name: col.type
            for col in self.model.__table__.columns
            if col.name != "id"
        }

    def _create_temp_table_like(
        self,
        session: Session | None = None,
        source_table: str | None = None,
    ) -> str:
        """
        Create a temporary MySQL table matching source table structure.

        Parameters:
            session (Session | None, optional): Session override. Defaults to self._session.
            source_table (str | None, optional): Source table name. Defaults to self.tablename.

        Returns:
            str: Name of created temporary table.
        """
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

    def _drop_temp_table(
        self,
        session: Session | None = None,
        temp_tablename: str | None = None
    ) -> None:
        """
        Drop a temporary MySQL staging table if it exists.

        Parameters:
            session (Session | None, optional): Session override. Defaults to self._session.
            temp_tablename (str | None, optional): Name of temporary table. Defaults to self.temp_tablename.
        """
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        sql = text(f"""
            DROP TEMPORARY TABLE IF EXISTS {temp_tablename}
        """)
        self._session.execute(sql)

    def _load_data_to_temp_table_from_csv(
        self,
        session: Session | None = None,
        file_path: str = "",
        columns: list[str] | None = None,
        temp_tablename: str | None = None
    ) -> str:
        """
        Load data into temporary staging table via MySQL `LOAD DATA LOCAL INFILE`.

        Parameters:
            session (Session | None, optional): Session override. Defaults to self._session.
            file_path (str): Path to CSV file.
            columns (list[str] | None, optional): List of target column names. Defaults to empty list.
            temp_tablename (str | None, optional): Target staging table name. Defaults to self.temp_tablename.

        Returns:
            str: Target temporary table name.
        """
        if not temp_tablename:
            temp_tablename = self.temp_tablename

        columns = columns or []
        column_sql = ", ".join(f"`{column}`" for column in columns)
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
