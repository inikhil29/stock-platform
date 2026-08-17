from enum import Enum


class FinancialDataSourceEnum(str, Enum):
    UPSTOX = "upstox"

    @classmethod
    def from_value(cls, value: str) -> "FinancialDataSourceEnum":
        return cls(value.strip().lower())
