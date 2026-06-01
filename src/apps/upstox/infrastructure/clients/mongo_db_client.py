from pymongo import MongoClient
from pymongo.database import Database

from apps.upstox.config.settings import settings


class MongoDBClient:

    _client: MongoClient | None = None

    @classmethod
    def get_client(cls) -> MongoClient:

        if cls._client is None:
            cls._client = MongoClient(

                settings.UPSTOX_MONGO_URI,

                # Pool Settings
                maxPoolSize=100,
                minPoolSize=10,

                # Timeouts
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,

                # Retry Handling
                retryWrites=True,
                retryReads=True,
            )

        return cls._client

    @classmethod
    def get_database(cls) -> Database:

        return cls.get_client()[settings.UPSTOX_MONGODB_DATABSE]
