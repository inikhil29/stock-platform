"""
Financial Statement Records Repository Module.

Manages data access and upserting for individual financial statement metric values
(e.g. Total Assets, Operating Expenses, Net Cash Flow) tied to specific financial statements and periods.
"""

from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.financial_statement_records import FinancialStatementRecords
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialStatementRecordsRepository(BasePostgresRepository[FinancialStatementRecords]):
    """
    PostgreSQL repository for `FinancialStatementRecords` time-series metric entries.

    Attributes:
        _model (type[FinancialStatementRecords]): Bound SQLAlchemy model class `FinancialStatementRecords`.
    """

    _model = FinancialStatementRecords

    def __init__(self, session: Session):
        """
        Initialize FinancialStatementRecordsRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(
        self,
        financial_statement_id: int,
        financial_period_type_id: int,
        finance_metric_id: int,
        value: float | int | Decimal
    ) -> int:
        """
        Upsert a financial statement metric observation and return its primary key ID.

        If a row matching (financial_statement_id, financial_period_type_id, finance_metric_id) exists,
        updates its `value` and `updated_at` fields.

        Parameters:
            financial_statement_id (int): Foreign key to the parent `financial_statements` row.
            financial_period_type_id (int): Foreign key to `financial_period_types` (fiscal date/quarter).
            finance_metric_id (int): Foreign key to `finance_metrics` (metric definition).
            value (float | int | Decimal): Numeric financial value (in statement denomination units).

        Returns:
            int: Primary key ID of the inserted or updated statement record.
        """
        insert_data = {
            self._model.financial_statement_id: financial_statement_id,
            self._model.financial_period_type_id: financial_period_type_id,
            self._model.finance_metric_id: finance_metric_id,
            self._model.value: value,
        }

        unique_columns = [
            self._model.financial_statement_id,
            self._model.financial_period_type_id,
            self._model.finance_metric_id,
        ]

        update_data = {
            self._model.value: value,
            self._model.updated_at: func.now()
        }

        result = self._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result
