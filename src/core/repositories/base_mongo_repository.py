"""
Base MongoDB Repository Module.

Provides generic CRUD, indexing, Pydantic validation, single upsert, and bulk write
operations for MongoDB document collections.
"""

from typing import Any
from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import BulkWriteResult, DeleteResult, UpdateResult


class BaseMongoRepository:
    """
    Generic repository for MongoDB collections integrated with Pydantic model validation.

    Attributes:
        model_class (type): Pydantic model class representing the collection schema.
        collection (Collection): PyMongo Collection handle.
    """

    def __init__(self, database: Database, model_class: type):
        """
        Initialize BaseMongoRepository with database connection and target Pydantic model.

        Parameters:
            database (Database): PyMongo Database instance.
            model_class (type): Pydantic model class defining `_collection_name` and optional `_indexes`.
        """
        self.model_class = model_class
        self.collection: Collection = database[model_class._collection_name]
        self.create_indexes()

    # ---------------------------------
    # INDEXES
    # ---------------------------------

    def create_indexes(self) -> None:
        """
        Create declared compound or single-field indexes on the collection.

        Reads the `_indexes` attribute on `model_class` and applies them with unique flags if set.
        """
        indexes = getattr(self.model_class, "_indexes", [])
        for index in indexes:
            self.collection.create_index(
                index["fields"],
                unique=index.get("unique", False)
            )

    # ---------------------------------
    # VALIDATION
    # ---------------------------------

    def validate_model(self, data: dict[str, Any]) -> Any:
        """
        Instantiate and validate raw dictionary data against the repository's Pydantic model.

        Parameters:
            data (dict[str, Any]): Raw document dictionary.

        Returns:
            Any: Validated Pydantic model instance.
        """
        return self.model_class(**data)

    # ---------------------------------
    # INSERT
    # ---------------------------------

    def insert_one(self, data: dict[str, Any]) -> str:
        """
        Validate and insert a single document into the collection.

        Parameters:
            data (dict[str, Any]): Document fields dictionary.

        Returns:
            str: Hex string representation of the generated MongoDB `_id`.
        """
        model = self.validate_model(data)
        result = self.collection.insert_one(
            model.model_dump(by_alias=True)
        )
        return str(result.inserted_id)

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records: list[dict[str, Any]]) -> list[str]:
        """
        Validate and insert multiple documents in a single bulk operation.

        Parameters:
            records (list[dict[str, Any]]): List of document dictionaries.

        Returns:
            list[str]: List of string `_id` values for all successfully inserted documents.
        """
        validated = []
        for record in records:
            try:
                model = self.validate_model(record)
                validated.append(
                    model.model_dump(by_alias=True)
                )
            except Exception as e:
                print(e)

        if not validated:
            return []

        result = self.collection.insert_many(validated)
        return [str(_id) for _id in result.inserted_ids]

    # ---------------------------------
    # UPSERT
    # ---------------------------------

    def upsert_one(
        self,
        query: dict[str, Any],
        data: dict[str, Any]
    ) -> UpdateResult:
        """
        Validate and upsert a single document matching the query filter using `$set`.

        Parameters:
            query (dict[str, Any]): MongoDB filter query for locating existing document.
            data (dict[str, Any]): Raw document fields to set upon insert or update.

        Returns:
            UpdateResult: PyMongo update result containing matched/modified/upserted counts.
        """
        model = self.validate_model(data)
        payload = model.model_dump(by_alias=True)
        payload.pop("_id", None)

        return self.collection.update_one(
            query,
            {"$set": payload},
            upsert=True
        )

    # ---------------------------------
    # BULK UPSERT
    # ---------------------------------

    def bulk_upsert(
        self,
        records: list[dict[str, Any]],
        unique_field: str
    ) -> BulkWriteResult | None:
        """
        Perform a bulk unordered upsert using `UpdateOne` operations grouped by a unique field.

        Parameters:
            records (list[dict[str, Any]]): List of document dictionaries.
            unique_field (str): Name of the key used to match existing documents (e.g. 'isin').

        Returns:
            BulkWriteResult | None: PyMongo bulk write execution summary, or None if no valid operations.
        """
        operations = []
        for record in records:
            try:
                model = self.validate_model(record)
                payload = model.model_dump(by_alias=True)
                operations.append(
                    UpdateOne(
                        {unique_field: payload[unique_field]},
                        {"$set": payload},
                        upsert=True
                    )
                )
            except Exception as e:
                print(e)

        if not operations:
            return None

        return self.collection.bulk_write(operations)

    # ---------------------------------
    # FIND
    # ---------------------------------

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """
        Find a single document matching the query filter.

        Parameters:
            query (dict[str, Any]): MongoDB query dictionary.

        Returns:
            dict[str, Any] | None: Found document dictionary or None.
        """
        return self.collection.find_one(query)

    def find_many(
        self,
        query: dict[str, Any],
        limit: int = 100,
        skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        Find multiple documents with pagination skip and limit.

        Parameters:
            query (dict[str, Any]): MongoDB query filter.
            limit (int, optional): Maximum documents to return. Defaults to 100.
            skip (int, optional): Number of documents to skip. Defaults to 0.

        Returns:
            list[dict[str, Any]]: List of matching document dictionaries.
        """
        return list(
            self.collection.find(query)
            .skip(skip)
            .limit(limit)
        )

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete_one(self, query: dict[str, Any]) -> DeleteResult:
        """
        Delete a single document matching the query filter.

        Parameters:
            query (dict[str, Any]): Filter specifying document to delete.

        Returns:
            DeleteResult: PyMongo delete execution result.
        """
        return self.collection.delete_one(query)
