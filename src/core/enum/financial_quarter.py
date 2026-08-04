from enum import Enum

class FinancialQuarter(str, Enum):
    Q1  = "q1"
    Q2  = "q2"
    Q3  = "q3"
    Q4  = "q4"

    @property
    def get_quarter(self) -> str:
        unit_map = {
            "q1": 1,
            "q2": 2,
            "q3": 3,
            "q4": 4,
        }
        return unit_map[self.value]
