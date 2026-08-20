from sqlalchemy import func, select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.financial_statement_records import FinancialStatementRecords
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialStatementRecordsRepository(
    BasePostgresRepository[FinancialStatementRecords]
):
    _model = FinancialStatementRecords

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def upsert_and_get_id(self, financial_statement_id: int, financial_period_type_id: int, finance_metric_id: int, value: int) -> int:
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
            self._model.updated_at: func.now()
        }

        result = super()._upsert_and_get_id(insert_data=insert_data,
                                            update_data=update_data, unique_columns=unique_columns)
        return result
