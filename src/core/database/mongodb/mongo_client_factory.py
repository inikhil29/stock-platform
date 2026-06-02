from pymongo import MongoClient


class MongoClientFactory:

    _clients = {}

    @classmethod
    def get_client(
        cls,
        mongo_uri: str
    ):

        if mongo_uri not in cls._clients:

            cls._clients[mongo_uri] = MongoClient(
                mongo_uri,
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

        return cls._clients[mongo_uri]
    