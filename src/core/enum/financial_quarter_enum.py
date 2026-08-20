from enum import Enum


class FinancialQuarter(str, Enum):
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"

    @property
    def get_quarter(self) -> str:
        unit_map = {
            "q1": 1,
            "q2": 2,
            "q3": 3,
            "q4": 4,
        }
        return unit_map[self.value]

    @classmethod
    def from_number(cls, number: int) -> "FinancialQuarter":
        return {
            1: FinancialQuarter.Q1,
            2: FinancialQuarter.Q2,
            3: FinancialQuarter.Q3,
            4: FinancialQuarter.Q4
        }[number]
