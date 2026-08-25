"""
Company Finance Services Module.

Responsible for parsing, transforming, and persisting corporate financial statements
(Balance Sheet, Cash Flow, Income Statement) from the Upstox Fundamental Data API into
normalized PostgreSQL financial statement tables.
"""

import calendar
from datetime import date, datetime
import logging
from typing import Any

from apps.stock_data_management.config.finance_matrics_alias_mapping import FINANCIAL_METRIC_ALIASES
from apps.stock_data_management.config.finance_units_alias_mapping import FINANCIAL_PRICE_UNITS_ALIASES
from apps.stock_data_management.infrastructure.clients.company_financial_data_client import CompanyFinancialDataClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.enum.financial_periods_enum import StatementPeriodTypes
from core.enum.financial_quarter_enum import FinancialQuarter
from core.enum.financial_statement_type_enum import FinancialStatmentType
from core.enum.price_unit_enum import PriceUnitEnum

logger = logging.getLogger(__name__)


class CompanyFinanceServices:
    """
    Service layer orchestrating the extraction and relational persistence of financial statements.

    Normalizes varying reporting units (e.g. Crores, Lakhs), period frequencies (annual, quarterly),
    and line item metric classifications across consolidated and standalone filings.

    Attributes:
        _unit_of_work (PostgresUnitOfWork): Unit of Work coordinating relational transactions.
        _stock_instrument_client (CompanyFinancialDataClient): Client communicating with Upstox financial API.
    """

    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_instrument_client: CompanyFinancialDataClient
    ):
        """
        Initialize the CompanyFinanceServices.

        Parameters:
            unit_of_work (PostgresUnitOfWork): Database Unit of Work instance for repository management.
            stock_instrument_client (CompanyFinancialDataClient): HTTP client communicating with Upstox API.
        """
        self._unit_of_work = unit_of_work
        self._stock_instrument_client = stock_instrument_client

    def parse_balance_sheet_from_upstox(
        self,
        isin: str,
        statement_type: str = 'consolidated'
    ) -> None:
        """
        Fetch, parse, and persist Balance Sheet statements for a company.

        Extracts line item metrics (assets, liabilities, equity) and their historical values
        across reporting periods, upserting corresponding records in PostgreSQL.

        Parameters:
            isin (str): 12-character International Securities Identification Number.
            statement_type (str, optional): Type of statement, either 'consolidated' or 'standalone'. Defaults to 'consolidated'.

        Raises:
            ValueError: If an unknown price unit or unrecognized financial metric alias is encountered.
        """
        get_balance_sheet_data = self._stock_instrument_client.get_balance_sheet_from_upstox(
            isin=isin,
            type=statement_type
        )
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source
            )
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]

            if price_units_in not in FINANCIAL_PRICE_UNITS_ALIASES:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

            price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
            financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                financial_report_price_unit=price_units_enum
            )
            finance_statement_type = FinancialStatmentType.from_value(
                statement_type)

            full_statement = get_balance_sheet_data["full_statement"]
            statement_id = uow.financial_statements_repository.upsert_and_get_id(
                finance_data_source_id=finance_data_source_id,
                isin=isin,
                financial_report_price_unit_id=financial_report_price_unit_id,
                finance_statement_type=finance_statement_type,
                financial_statement_period_type=statement_period_type,
            )

            for line_item in full_statement:
                particular = line_item["particular"]
                if particular not in FINANCIAL_METRIC_ALIASES:
                    raise ValueError(
                        f"FINANCIAL METRIC NOT FOUND: {particular}")

                metric_code = FINANCIAL_METRIC_ALIASES[particular]
                finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                    metric_code=metric_code,
                    display_name=particular
                )
                history_data = line_item["history"]
                for record in history_data:
                    period = record["period"]
                    value = record["value"]
                    end_date = self._get_end_date_from_str(period)
                    financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                        financial_period_type=financial_period,
                        end_date=end_date
                    )

                    uow.financial_statement_records_repository.upsert_and_get_id(
                        financial_statement_id=statement_id,
                        financial_period_type_id=financial_period_type_id,
                        finance_metric_id=finance_metric_id,
                        value=value
                    )

    def parse_cash_flow_data_from_upstox(
        self,
        isin: str,
        statement_type: str = 'consolidated'
    ) -> None:
        """
        Fetch, parse, and persist Cash Flow statements for a company.

        Processes operating, investing, and financing cash flow categories as well
        as full statement breakdowns.

        Parameters:
            isin (str): 12-character International Securities Identification Number.
            statement_type (str, optional): Filing type ('consolidated' or 'standalone'). Defaults to 'consolidated'.

        Raises:
            ValueError: If an unknown price unit or unrecognized financial metric alias is encountered.
        """
        get_balance_sheet_data = self._stock_instrument_client.get_cash_flow_from_upstox(
            isin=isin,
            type=statement_type
        )
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source
            )
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]

            if price_units_in not in FINANCIAL_PRICE_UNITS_ALIASES:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

            price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
            financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                financial_report_price_unit=price_units_enum
            )
            finance_statement_type = FinancialStatmentType.from_value(
                statement_type)

            statement_id = uow.financial_statements_repository.upsert_and_get_id(
                finance_data_source_id=finance_data_source_id,
                isin=isin,
                financial_report_price_unit_id=financial_report_price_unit_id,
                finance_statement_type=finance_statement_type,
                financial_statement_period_type=statement_period_type,
            )

            cash_flow_items = get_balance_sheet_data["cash_flow"]

            for line_item in cash_flow_items:
                category = line_item["category"]
                if category not in FINANCIAL_METRIC_ALIASES:
                    raise ValueError(f"FINANCIAL METRIC NOT FOUND: {category}")

                metric_code = FINANCIAL_METRIC_ALIASES[category]
                finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                    metric_code=metric_code,
                    display_name=category
                )
                if finance_metric_id:
                    history_data = line_item["history"]
                    for record in history_data:
                        period = record["period"]
                        value = record["value"]
                        end_date = self._get_end_date_from_str(period)
                        financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                            financial_period_type=financial_period,
                            end_date=end_date
                        )

                        uow.financial_statement_records_repository.upsert_and_get_id(
                            financial_statement_id=statement_id,
                            financial_period_type_id=financial_period_type_id,
                            finance_metric_id=finance_metric_id,
                            value=value
                        )

            full_statement = get_balance_sheet_data["full_statement"]

            for line_item in full_statement:
                particular = line_item["particular"]
                if particular not in FINANCIAL_METRIC_ALIASES:
                    raise ValueError(
                        f"FINANCIAL METRIC NOT FOUND: {particular}")

                metric_code = FINANCIAL_METRIC_ALIASES[particular]
                finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                    metric_code=metric_code,
                    display_name=particular
                )
                if finance_metric_id:
                    history_data = line_item["history"]
                    for record in history_data:
                        period = record["period"]
                        value = record["value"]
                        end_date = self._get_end_date_from_str(period)
                        financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                            financial_period_type=financial_period,
                            end_date=end_date
                        )

                        uow.financial_statement_records_repository.upsert_and_get_id(
                            financial_statement_id=statement_id,
                            financial_period_type_id=financial_period_type_id,
                            finance_metric_id=finance_metric_id,
                            value=value
                        )

    def parse_income_statement_data_from_upstox(
        self,
        isin: str,
        statement_type: str = 'consolidated'
    ) -> None:
        """
        Fetch, parse, and persist Income Statement (P&L) data for a company.

        Processes both quarterly income statement snapshots and full annual statements.

        Parameters:
            isin (str): 12-character International Securities Identification Number.
            statement_type (str, optional): Filing type ('consolidated' or 'standalone'). Defaults to 'consolidated'.

        Raises:
            ValueError: If an unknown price unit or unrecognized financial metric alias is encountered.
        """
        time_period = 'quarterly'
        get_balance_sheet_data = self._stock_instrument_client.get_income_statement_from_upstox(
            isin=isin,
            type=statement_type,
            time_period=time_period
        )
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source
            )
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]

            if price_units_in not in FINANCIAL_PRICE_UNITS_ALIASES:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

            price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
            financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                financial_report_price_unit=price_units_enum
            )
            finance_statement_type = FinancialStatmentType.from_value(
                statement_type)

            statement_id = uow.financial_statements_repository.upsert_and_get_id(
                finance_data_source_id=finance_data_source_id,
                isin=isin,
                financial_report_price_unit_id=financial_report_price_unit_id,
                finance_statement_type=finance_statement_type,
                financial_statement_period_type=statement_period_type,
            )

            income_statement_items = get_balance_sheet_data["income_statement"]

            for line_item in income_statement_items:
                category = line_item["category"]
                if category not in FINANCIAL_METRIC_ALIASES:
                    raise ValueError(f"FINANCIAL METRIC NOT FOUND: {category}")

                metric_code = FINANCIAL_METRIC_ALIASES[category]
                finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                    metric_code=metric_code,
                    display_name=category
                )

                history_data = line_item["history"]
                for record in history_data:
                    period = record["period"]
                    value = record["value"]
                    end_date = self._get_end_date_from_str(period)
                    quarter = self._get_the_qarter_from_date(
                        end_date) if time_period == 'quarterly' else None
                    financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                        financial_period_type=financial_period,
                        end_date=end_date,
                        quarter=quarter
                    )

                    uow.financial_statement_records_repository.upsert_and_get_id(
                        financial_statement_id=statement_id,
                        financial_period_type_id=financial_period_type_id,
                        finance_metric_id=finance_metric_id,
                        value=value
                    )

            full_statement = get_balance_sheet_data["full_statement"]

            # For Full statement, set the time period to yearly
            time_period = 'yearly'
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            statement_id = uow.financial_statements_repository.upsert_and_get_id(
                finance_data_source_id=finance_data_source_id,
                isin=isin,
                financial_report_price_unit_id=financial_report_price_unit_id,
                finance_statement_type=finance_statement_type,
                financial_statement_period_type=statement_period_type,
            )

            for line_item in full_statement:
                particular = line_item["particular"]
                if particular not in FINANCIAL_METRIC_ALIASES:
                    raise ValueError(
                        f"FINANCIAL METRIC NOT FOUND: {particular}")

                metric_code = FINANCIAL_METRIC_ALIASES[particular]
                finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                    metric_code=metric_code,
                    display_name=particular
                )

                history_data = line_item["history"]
                for record in history_data:
                    period = record["period"]
                    value = record["value"]
                    end_date = self._get_end_date_from_str(period)
                    quarter = self._get_the_qarter_from_date(
                        end_date) if time_period == 'quarterly' else None
                    financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                        financial_period_type=financial_period,
                        end_date=end_date,
                        quarter=quarter
                    )

                    uow.financial_statement_records_repository.upsert_and_get_id(
                        financial_statement_id=statement_id,
                        financial_period_type_id=financial_period_type_id,
                        finance_metric_id=finance_metric_id,
                        value=value
                    )

    def _get_end_date_from_str(self, date_string: str) -> date:
        """
        Parse a string period in '%b %Y' format (e.g. 'Mar 2024') and return the month's last calendar date.

        Parameters:
            date_string (str): Date string formatted as '%b %Y' (e.g. 'Dec 2023').

        Returns:
            date: Exact ending date object for that calendar month (e.g. 2023-12-31).
        """
        date_obj = datetime.strptime(date_string, '%b %Y')
        year = date_obj.year
        month = date_obj.month
        _, last_day_of_month = calendar.monthrange(year, month)
        return date(year, month, last_day_of_month)

    def _get_the_qarter_from_date(self, date_obj: date) -> FinancialQuarter:
        """
        Compute the financial quarter enum (Q1..Q4) based on the month of a date.

        Parameters:
            date_obj (date): Calendar date.

        Returns:
            FinancialQuarter: FinancialQuarter enum instance.
        """
        month = date_obj.month
        quarter = - (- month // 3)
        return FinancialQuarter.from_number(quarter)
