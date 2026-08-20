from enum import Enum
from typing import Optional


class PriceUnitEnum(Enum):
    THOUSAND = 1000
    LAKH = 100000
    MILLION = 1000000
    CRORE = 10000000
    BILLION = 1000000000

    @classmethod
    def from_units(cls, value: str) -> Optional["PriceUnitEnum"]:
        try:
            return PriceUnitEnum[value.upper()]
        except KeyError:
            return None
