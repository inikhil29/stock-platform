from pydantic import Field

from core.models.mongo_base import (
    MongoBaseModel
)
from typing import ClassVar
from pydantic import BaseModel
from core.models.mongo_base import (
    MongoBaseModel
)


class MarketCap(BaseModel):

    value: float

    unit: str

    formatted: str


class StockInstrumentsProfile(MongoBaseModel):

    _collection_name: ClassVar[str] = (
        "stock_instruments_profile"
    )
    _indexes: ClassVar[list] = [
        {
            "fields": ["instrument_id"],
            "unique": True
        },
        {
            "fields": ["instrument_key"],
            "unique": True
        },
        {
            "fields": ["sector"],
            "unique": False
        },
        {
            "fields": ["created_at"],
            "unique": False
        }

    ]

    instrument_key: str

    instrument_id: int

    company_profile: str | None

    sector: str | None

    sector_market_cap_inr: MarketCap

    sector_market_cap_usd: MarketCap
