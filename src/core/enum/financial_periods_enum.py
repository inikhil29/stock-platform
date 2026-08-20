from enum import Enum


class FinancialPeriod(str, Enum):
    Y = "y"
    Q = "q"
    M = "m"


class StatementPeriodTypes(str, Enum):
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"

    @classmethod
    def from_value(cls, value: str) -> "StatementPeriodTypes":
        return cls(value.strip().lower())

    @property
    def financial_period(self) -> FinancialPeriod:
        return {
            StatementPeriodTypes.YEARLY: FinancialPeriod.Y,
            StatementPeriodTypes.QUARTERLY: FinancialPeriod.Q,
            StatementPeriodTypes.MONTHLY: FinancialPeriod.M,
        }[self]
