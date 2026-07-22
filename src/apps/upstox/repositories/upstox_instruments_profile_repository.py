from core.repositories.base_mongo_repository import BaseMongoRepository



class UpstoxInstrumentsProfileRepository(BaseMongoRepository):

    def __init__(self, database, model):

        super().__init__(database, model)
