"""
Finance Metrics Repository Module.

Manages data access and upserting for financial statement line item metric codes
(e.g. Total Revenue, Net Income, Operating Cash Flow) in PostgreSQL.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.finance_metrics import FinanceMetrics
from core.enum.finance_metrics_enum import FinancialMetric
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinanceMetricsRepository(BasePostgresRepository[FinanceMetrics]):
    """
    PostgreSQL repository for `FinanceMetrics` master records.

    Attributes:
        _model (type[FinanceMetrics]): Bound SQLAlchemy model class `FinanceMetrics`.
    """

    _model = FinanceMetrics

    def __init__(self, session: Session):
        """
        Initialize FinanceMetricsRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def get_id_from_metric_code(self, metric_code: FinancialMetric) -> int | None:
        """
        Look up the primary key ID for a financial metric code.

        Parameters:
            metric_code (FinancialMetric): Normalized metric enum identifier.

        Returns:
            int | None: Primary key ID if found, None otherwise.
        """
        stmt = select(self._model.finance_metric_id).where(
            self._model.metric_code == metric_code
        )
        return self._session.scalar(stmt)

    def upsert_and_get_id(
        self,
        metric_code: FinancialMetric,
        display_name: str | None = None
    ) -> int:
        """
        Upsert a financial metric definition and return its primary key ID.

        Parameters:
            metric_code (FinancialMetric): Normalized metric enum identifier.
            display_name (str | None, optional): Human-readable metric display name. Defaults to None.

        Returns:
            int: Primary key ID of the metric record.
        """
        insert_data = {
            self._model.metric_code: metric_code,
            self._model.display_name: display_name,
        }

        unique_columns = [
            self._model.metric_code,
        ]
        update_data = {
            self._model.updated_at: func.now()
        }

        result = super()._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result
