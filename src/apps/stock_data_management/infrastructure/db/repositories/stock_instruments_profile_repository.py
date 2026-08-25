"""
Stock Instruments Profile Repository Module.

Manages data access for MongoDB document storage of unstructured
company fundamental profiles, sector classifications, and market cap figures.
"""

from pymongo.database import Database
from core.repositories.base_mongo_repository import BaseMongoRepository


class StockInstrumentsProfileRepository(BaseMongoRepository):
    """
    MongoDB repository for the `stock_instruments_profile` collection.

    Inherits CRUD and bulk upsert operations from `BaseMongoRepository`.
    """

    def __init__(self, database: Database, model: type):
        """
        Initialize StockInstrumentsProfileRepository with database handle and Pydantic model.

        Parameters:
            database (Database): Active PyMongo database connection.
            model (type): `StockInstrumentsProfile` Pydantic model class.
        """
        super().__init__(database=database, model_class=model)
