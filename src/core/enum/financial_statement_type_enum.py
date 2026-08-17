from enum import Enum


class FinancialStatmentType(str, Enum):
    STANDALONE   = "standalone"
    CONSOLIDATED   = "consolidated"

    @classmethod
    def from_value(cls, value: str) -> "FinancialStatmentType":
        return cls(value.strip().lower())
