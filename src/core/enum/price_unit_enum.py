from enum import Enum


class PriceUnitEnum(Enum):
    THOUSAND = 1000
    HUNDRED_THOUSAND = 100000
    LAKH = 100000
    MILLION = 1000000
    CRORE = 10000000
    BILLION = 1000000000

    @classmethod
    def from_units(cls, value: str) -> "PriceUnitEnum" | None:
        try:
            return PriceUnitEnum[value.upper()]
        except KeyError:
            return None
