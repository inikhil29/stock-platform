from apps.nse.config.settings import settings
from core.infrastructure.database.mongodb.mongo_client_factory import MongoClientFactory


def get_database():

    client = (
        MongoClientFactory.get_client(
            settings.UPSTOX_MONGO_URI
        )
    )

    return client[
        settings.UPSTOX_MONGODB_DATABASE
    ]
