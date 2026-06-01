from pymongo.collection import Collection
from pymongo import UpdateOne

from apps.upstox.infrastructure.clients.mongo_db_client import (
    MongoDBClient
)


class BaseMongoRepository:

    def __init__(self, model_class):

        self.model_class = model_class

        db = MongoDBClient.get_database()

        self.collection: Collection = db[
            model_class._collection_name
        ]

        self.create_indexes()

    # ---------------------------------
    # INDEXES
    # ---------------------------------
    def create_indexes(self):

        indexes = getattr(
            self.model_class,
            "_indexes",
            []
        )

        for index in indexes:

            self.collection.create_index(
                index["fields"],
                unique=index.get(
                    "unique",
                    False
                )
            )

    # ---------------------------------
    # VALIDATION
    # ---------------------------------
    def validate_model(self, data):

        return self.model_class(**data)

    # ---------------------------------
    # INSERT
    # ---------------------------------
    def insert_one(self, data):

        model = self.validate_model(data)

        result = self.collection.insert_one(
            model.model_dump(by_alias=True)
        )

        return str(result.inserted_id)

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------
    def insert_many(self, records):

        validated = []

        for record in records:

            try:

                model = self.validate_model(
                    record
                )

                validated.append(
                    model.model_dump(
                        by_alias=True
                    )
                )

            except Exception as e:

                print(e)

        if not validated:
            return []

        result = self.collection.insert_many(
            validated
        )

        return [
            str(_id)
            for _id in result.inserted_ids
        ]

    # ---------------------------------
    # UPSERT
    # ---------------------------------
    def upsert_one(
        self,
        query,
        data
    ):
        model = self.validate_model(data)
        payload = model.model_dump(
            by_alias=True
        )
        payload.pop("_id", None)

        return self.collection.update_one(
            query,
            {
                "$set":payload
            },
            upsert=True
        )

    # ---------------------------------
    # BULK UPSERT
    # ---------------------------------
    def bulk_upsert(
        self,
        records,
        unique_field
    ):

        operations = []

        for record in records:

            try:

                model = self.validate_model(
                    record
                )

                payload = model.model_dump(
                    by_alias=True
                )

                operations.append(

                    UpdateOne(
                        {
                            unique_field:
                            payload[unique_field]
                        },
                        {
                            "$set": payload
                        },
                        upsert=True
                    )
                )

            except Exception as e:

                print(e)

        if not operations:
            return None

        return self.collection.bulk_write(
            operations
        )

    # ---------------------------------
    # FIND
    # ---------------------------------
    def find_one(self, query):

        return self.collection.find_one(query)

    def find_many(
        self,
        query,
        limit=100,
        skip=0
    ):

        return list(
            self.collection.find(query)
            .skip(skip)
            .limit(limit)
        )

    # ---------------------------------
    # DELETE
    # ---------------------------------
    def delete_one(self, query):

        return self.collection.delete_one(
            query
        )
