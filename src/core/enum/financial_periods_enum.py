from enum import Enum

class FinancialPeriod(str, Enum):
    Y   = "y"
    Q   = "q"
    M   = "m"

    @property
    def unit(self) -> str:
        unit_map = {
            "y": "years",
            "q": "quarter",
            "m": "months",
        }
        return unit_map[self.value]
