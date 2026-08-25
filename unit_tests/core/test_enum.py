"""
Unit tests for Core domain enums.
"""

import pytest
from core.enum.candle_interval_enum import CandleInterval
from core.enum.finance_metrics_enum import FinancialMetric
from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.enum.financial_periods_enum import FinancialPeriod, StatementPeriodTypes
from core.enum.financial_quarter_enum import FinancialQuarter
from core.enum.financial_statement_type_enum import FinancialStatmentType
from core.enum.price_unit_enum import PriceUnitEnum


class TestFinancialQuarterEnum:
    """Test suite for FinancialQuarter enumeration methods."""

    def test_enum_values(self):
        assert FinancialQuarter.Q1.value == "q1"
        assert FinancialQuarter.Q2.value == "q2"
        assert FinancialQuarter.Q3.value == "q3"
        assert FinancialQuarter.Q4.value == "q4"

    def test_get_quarter_property(self):
        assert FinancialQuarter.Q1.get_quarter == 1
        assert FinancialQuarter.Q2.get_quarter == 2
        assert FinancialQuarter.Q3.get_quarter == 3
        assert FinancialQuarter.Q4.get_quarter == 4

    def test_from_number(self):
        assert FinancialQuarter.from_number(1) == FinancialQuarter.Q1
        assert FinancialQuarter.from_number(2) == FinancialQuarter.Q2
        assert FinancialQuarter.from_number(3) == FinancialQuarter.Q3
        assert FinancialQuarter.from_number(4) == FinancialQuarter.Q4

    def test_from_number_invalid(self):
        with pytest.raises(KeyError):
            FinancialQuarter.from_number(5)


class TestCandleIntervalEnum:
    """Test suite for CandleInterval resolution options."""

    def test_interval_values(self):
        assert CandleInterval.M1.value == "1m"
        assert CandleInterval.M5.value == "5m"
        assert CandleInterval.D1.value == "1d"
        assert CandleInterval.W1.value == "1w"
        assert CandleInterval.MN1.value == "1mo"

    def test_interval_properties(self):
        assert CandleInterval.M1.interval_option == 1
        assert CandleInterval.M1.unit == "minutes"
        assert CandleInterval.D1.interval_option == 1
        assert CandleInterval.D1.unit == "days"


class TestFinancialEnums:
    """Test suite for master financial taxonomy enums."""

    def test_data_sources(self):
        assert FinancialDataSourceEnum.UPSTOX.value == "upstox"

    def test_statement_types(self):
        assert FinancialStatmentType.CONSOLIDATED.value == "consolidated"
        assert FinancialStatmentType.STANDALONE.value == "standalone"

    def test_price_units(self):
        assert PriceUnitEnum.CRORE.value == 10000000
        assert PriceUnitEnum.LAKH.value == 100000
        assert PriceUnitEnum.THOUSAND.value == 1000
        assert PriceUnitEnum.from_units("CRORE") == PriceUnitEnum.CRORE
        assert PriceUnitEnum.from_units("INVALID") is None

    def test_financial_periods(self):
        assert FinancialPeriod.Y.value == "y"
        assert FinancialPeriod.Q.value == "q"
        assert StatementPeriodTypes.YEARLY.value == "yearly"
        assert StatementPeriodTypes.QUARTERLY.value == "quarterly"
        assert StatementPeriodTypes.YEARLY.financial_period == FinancialPeriod.Y

    def test_financial_metric_enum(self):
        assert FinancialMetric.TOTAL_REVENUE.value == "TOTAL_REVENUE"
        assert FinancialMetric.OTHER_INCOME.value == "OTHER_INCOME"
        assert FinancialMetric.TOTAL_ASSETS.value == "TOTAL_ASSETS"

