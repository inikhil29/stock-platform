from enum import Enum
import re


class CandleInterval(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"

    H1 = "1h"
    H2 = "2h"
    H4 = "4h"

    D1 = "1d"
    W1 = "1w"
    MN1 = "1mo"

    @property
    def interval_option(self) -> int:
        return int(re.findall(r'\d+', self.value)[0])

    @property
    def unit(self) -> str:
        unit_map = {
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks",
            "mo": "months",
        }
        return unit_map[re.findall(r'\D+', self.value)[0]]
