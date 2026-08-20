from sqlalchemy import func, select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.finance_metrics import FinanceMetrics
from core.enum.finance_metrics_enum import FinancialMetric
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinanceMetricsRepository(
    BasePostgresRepository[FinanceMetrics]
):
    _model = FinanceMetrics

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def get_id_from_metric_code(self, metric_code: FinancialMetric) -> int:
        stmt = select(self._model.finance_metric_id).where(
            self._model.metric_code == metric_code)
        return self._session.scalar(stmt)

    def upsert_and_get_id(self, metric_code: FinancialMetric, display_name: str | None = None) -> int:
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

        result = super()._upsert_and_get_id(insert_data=insert_data,
                                            update_data=update_data, unique_columns=unique_columns)
        return result
