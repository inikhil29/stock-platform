from core.repositories.base_mongo_repository import BaseMongoRepository
from apps.upstox.models.instruments_profile import (
    UpstoxInstrumentsProfile
)


class UpstoxInstrumentsProfileRepository(BaseMongoRepository):

    def __init__(self, database):

        super().__init__(database, UpstoxInstrumentsProfile)
