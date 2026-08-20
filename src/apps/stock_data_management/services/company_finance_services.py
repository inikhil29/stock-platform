import calendar
from datetime import datetime, date

from apps.stock_data_management.config.finance_matrics_alias_mapping import FINANCIAL_METRIC_ALIASES
from apps.stock_data_management.config.finance_units_alias_mapping import FINANCIAL_PRICE_UNITS_ALIASES
from apps.stock_data_management.infrastructure.clients.company_financial_data_client import CompanyFinancialDataClient
from apps.stock_data_management.infrastructure.db.postgres_unit_of_work import PostgresUnitOfWork
from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.enum.financial_periods_enum import StatementPeriodTypes
from core.enum.financial_quarter_enum import FinancialQuarter
from core.enum.financial_statement_type_enum import FinancialStatmentType
from core.enum.price_unit_enum import PriceUnitEnum


class CompanyFinanceServices:
    def __init__(
        self,
        unit_of_work: PostgresUnitOfWork,
        stock_instrument_client: CompanyFinancialDataClient
    ):

        self._unit_of_work = unit_of_work
        self._stock_instrument_client = stock_instrument_client

    def parse_balance_sheet_from_upstox(self, isin: str, statement_type: str = 'consolidated') -> None:
        get_balance_sheet_data = self._stock_instrument_client.get_balance_sheet_from_upstox(
            isin=isin, type=statement_type)
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source)
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]
            if price_units_in in FINANCIAL_PRICE_UNITS_ALIASES:
                price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
                financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                    financial_report_price_unit=price_units_enum)
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
                    if particular in FINANCIAL_METRIC_ALIASES:
                        metric_code = FINANCIAL_METRIC_ALIASES[particular]
                        finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                            metric_code=metric_code, display_name=particular)
                        history_data = line_item["history"]
                        for record in history_data:
                            period = record["period"]
                            value = record["value"]
                            end_date = self._get_end_date_from_str(period)
                            financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                                financial_period_type=financial_period, end_date=end_date)

                            uow.financial_statement_records_repository.upsert_and_get_id(
                                financial_statement_id=statement_id,
                                financial_period_type_id=financial_period_type_id,
                                finance_metric_id=finance_metric_id,
                                value=value
                            )

                    else:
                        raise ValueError(
                            f"FINANCIAL METRIC NOT FOUND: {particular}")
            else:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

    def parse_cash_flow_data_from_upstox(self, isin: str, statement_type: str = 'consolidated') -> None:
        get_balance_sheet_data = self._stock_instrument_client.get_cash_flow_from_upstox(
            isin=isin, type=statement_type)
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source)
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]
            if price_units_in in FINANCIAL_PRICE_UNITS_ALIASES:
                price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
                financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                    financial_report_price_unit=price_units_enum)
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
                    if category in FINANCIAL_METRIC_ALIASES:
                        metric_code = FINANCIAL_METRIC_ALIASES[category]
                        finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                            metric_code=metric_code, display_name=category)
                        if finance_metric_id:
                            history_data = line_item["history"]
                            for record in history_data:
                                period = record["period"]
                                value = record["value"]
                                end_date = self._get_end_date_from_str(
                                    period)
                                financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                                    financial_period_type=financial_period, end_date=end_date)

                                uow.financial_statement_records_repository.upsert_and_get_id(
                                    financial_statement_id=statement_id,
                                    financial_period_type_id=financial_period_type_id,
                                    finance_metric_id=finance_metric_id,
                                    value=value
                                )

                    else:
                        raise ValueError(
                            f"FINANCIAL METRIC NOT FOUND: {category}"
                        )

                full_statement = get_balance_sheet_data["full_statement"]

                for line_item in full_statement:
                    particular = line_item["particular"]
                    if particular in FINANCIAL_METRIC_ALIASES:
                        metric_code = FINANCIAL_METRIC_ALIASES[particular]
                        finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                            metric_code=metric_code, display_name=particular)
                        if finance_metric_id:
                            history_data = line_item["history"]
                            for record in history_data:
                                period = record["period"]
                                value = record["value"]
                                end_date = self._get_end_date_from_str(
                                    period)
                                financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                                    financial_period_type=financial_period, end_date=end_date)

                                uow.financial_statement_records_repository.upsert_and_get_id(
                                    financial_statement_id=statement_id,
                                    financial_period_type_id=financial_period_type_id,
                                    finance_metric_id=finance_metric_id,
                                    value=value
                                )
                    else:
                        raise ValueError(
                            f"FINANCIAL METRIC NOT FOUND: {particular}"
                        )

            else:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

    def parse_income_statement_data_from_upstox(self, isin: str, statement_type: str = 'consolidated') -> None:
        time_period = 'quarterly'
        get_balance_sheet_data = self._stock_instrument_client.get_income_statement_from_upstox(
            isin=isin, type=statement_type, time_period=time_period)
        finance_data_source = FinancialDataSourceEnum.UPSTOX

        with self._unit_of_work as uow:
            finance_data_source_id = uow.finace_data_source_repository.upsert_and_get_id(
                finance_data_source)
            time_period = get_balance_sheet_data["time_period"]
            statement_period_type = StatementPeriodTypes.from_value(
                time_period)
            financial_period = statement_period_type.financial_period
            price_units_in = get_balance_sheet_data["units_in"]
            if price_units_in in FINANCIAL_PRICE_UNITS_ALIASES:
                price_units_enum = FINANCIAL_PRICE_UNITS_ALIASES[price_units_in]
                financial_report_price_unit_id = uow.financial_report_price_units_repository.upsert_and_get_id(
                    financial_report_price_unit=price_units_enum)
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
                    if category in FINANCIAL_METRIC_ALIASES:
                        metric_code = FINANCIAL_METRIC_ALIASES[category]
                        finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                            metric_code=metric_code, display_name=category)

                        history_data = line_item["history"]
                        for record in history_data:
                            period = record["period"]
                            value = record["value"]
                            end_date = self._get_end_date_from_str(
                                period)
                            quarter = self._get_the_qarter_from_date(
                                end_date) if time_period == 'quarterly' else None
                            financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                                financial_period_type=financial_period, end_date=end_date, quarter=quarter)

                            uow.financial_statement_records_repository.upsert_and_get_id(
                                financial_statement_id=statement_id,
                                financial_period_type_id=financial_period_type_id,
                                finance_metric_id=finance_metric_id,
                                value=value
                            )

                full_statement = get_balance_sheet_data["full_statement"]

                # For Full statement setting the time period yeraly
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
                    if particular in FINANCIAL_METRIC_ALIASES:
                        metric_code = FINANCIAL_METRIC_ALIASES[particular]
                        finance_metric_id = uow.finance_metrics_repository.upsert_and_get_id(
                            metric_code=metric_code, display_name=particular)

                        history_data = line_item["history"]
                        for record in history_data:
                            period = record["period"]
                            value = record["value"]
                            end_date = self._get_end_date_from_str(
                                period)
                            quarter = self._get_the_qarter_from_date(
                                end_date) if time_period == 'quarterly' else None
                            financial_period_type_id = uow.financial_period_types_repository.upsert_and_get_id(
                                financial_period_type=financial_period, end_date=end_date, quarter=quarter)

                            uow.financial_statement_records_repository.upsert_and_get_id(
                                financial_statement_id=statement_id,
                                financial_period_type_id=financial_period_type_id,
                                finance_metric_id=finance_metric_id,
                                value=value
                            )
            else:
                raise ValueError(f"PRICE UNIT NOT FOUND: {price_units_in}")

    def _get_end_date_from_str(self, date_string: str) -> date:
        date_obj = datetime.strptime(date_string, '%b %Y')
        year = date_obj.year
        month = date_obj.month
        _, last_day_of_month = calendar.monthrange(year, month)
        end_date = date(year, month, last_day_of_month)
        return end_date

    def _get_the_qarter_from_date(self, date_obj: date):
        month = date_obj.month
        quarter = - (- month // 3)
        return FinancialQuarter.from_number(quarter)
