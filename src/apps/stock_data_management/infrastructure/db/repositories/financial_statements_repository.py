from sqlalchemy import func, select, exists
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialStatementRepository(
    BasePostgresRepository[FinancialStatement]
):
    _model = FinancialStatement

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def upsert_and_get_id(self, finance_data_source_id, isin, financial_report_price_unit_id, finance_statement_type, financial_statement_period_type) -> int:
        insert_data = {
            self._model.finance_data_source_id: finance_data_source_id,
            self._model.isin: isin,
            self._model.financial_report_price_unit_id: financial_report_price_unit_id,
            self._model.finance_statement_type: finance_statement_type,
            self._model.financial_statement_period_type: financial_statement_period_type,
        }

        unique_columns = [
            self._model.finance_data_source_id,
            self._model.isin,
            self._model.financial_report_price_unit_id,
            self._model.finance_statement_type,
            self._model.financial_statement_period_type,
        ]

        update_data = {
            self._model.updated_at: func.now()
        }
        
        result = super()._upsert_and_get_id(insert_data=insert_data, update_data=update_data, unique_columns=unique_columns)
        return result
