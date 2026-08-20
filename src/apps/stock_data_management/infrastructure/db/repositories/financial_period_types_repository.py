from datetime import date

from sqlalchemy import func, select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.financial_period_types import FinancialPeriodTypes
from core.enum.financial_periods_enum import FinancialPeriod
from core.enum.financial_quarter_enum import FinancialQuarter
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialPeriodTypesRepository(
    BasePostgresRepository[FinancialPeriodTypes]
):
    _model: FinancialPeriodTypes = FinancialPeriodTypes

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def upsert_and_get_id(self, financial_period_type: FinancialPeriod, end_date: date, quarter: FinancialQuarter | None = None) -> int:
        insert_data = {
            self._model.financial_period_type: financial_period_type,
            self._model.end_date: end_date,
        }

        unique_columns = [
            self._model.financial_period_type,
            self._model.end_date,
        ]

        if quarter is not None:
            insert_data[self._model.quarter] = quarter

        update_data = {
            self._model.updated_at: func.now()
        }

        result = super()._upsert_and_get_id(insert_data=insert_data,
                                            update_data=update_data, unique_columns=unique_columns)
        return result
