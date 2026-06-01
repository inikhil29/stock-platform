from pydantic import Field
from pydantic import ConfigDict
from pydantic import BaseModel
from typing import ClassVar
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo


from pydantic import BaseModel, Field

timezone = ZoneInfo("Asia/Kolkata")

class MongoBaseModel(BaseModel):

    # Explicit collection name
    _collection_name: ClassVar[str]

    # MongoDB _id
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        alias="_id"
    )

    # Audit Fields
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone)
    )

    # Pydantic V2 Config
    model_config = ConfigDict(

        # Allow alias usage (_id)
        populate_by_name=True,

        # Validate assignment updates
        validate_assignment=True,

        # Ignore extra unexpected fields
        extra="ignore",

        # Allow arbitrary BSON types if needed
        arbitrary_types_allowed=True
    )

    @classmethod
    def get_collection_name(cls) -> str:

        return cls._collection_name

    def to_mongo(self) -> dict:

        return self.model_dump(
            by_alias=True,
            exclude_none=True
        )

    @classmethod
    def from_mongo(
        cls,
        document: dict
    ):

        if not document:
            return None

        return cls(**document)

    def touch(self):

        self.updated_at = datetime.now(timezone)
        
        
        
def _now_ist():
    return datetime.now(timezone)
