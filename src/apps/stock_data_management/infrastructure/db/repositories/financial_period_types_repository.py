"""
Financial Period Types Repository Module.

Manages data access and upserting for financial statement period definitions
(Annual, Quarterly, Half-Yearly) with date boundaries and quarter numbers.
"""

from datetime import date
from typing import ClassVar

from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.financial_period_types import FinancialPeriodTypes
from core.enum.financial_periods_enum import FinancialPeriod
from core.enum.financial_quarter_enum import FinancialQuarter
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialPeriodTypesRepository(BasePostgresRepository[FinancialPeriodTypes]):
    """
    PostgreSQL repository for `FinancialPeriodTypes` records.

    Attributes:
        _model (ClassVar[type[FinancialPeriodTypes]]): Bound SQLAlchemy model class `FinancialPeriodTypes`.
    """

    _model: ClassVar[type[FinancialPeriodTypes]] = FinancialPeriodTypes

    def __init__(self, session: Session):
        """
        Initialize FinancialPeriodTypesRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(
        self,
        financial_period_type: FinancialPeriod,
        end_date: date,
        quarter: FinancialQuarter | None = None
    ) -> int:
        """
        Upsert a financial period record (e.g. Q3 ending 2023-12-31) and return its primary key ID.

        Parameters:
            financial_period_type (FinancialPeriod): Frequency type enum (e.g. FinancialPeriod.YEARLY, FinancialPeriod.QUARTERLY).
            end_date (date): Calendar period end date.
            quarter (FinancialQuarter | None, optional): Financial quarter enum if quarterly statement. Defaults to None.

        Returns:
            int: Primary key ID of the financial period type record.
        """
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

        result = super()._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result
