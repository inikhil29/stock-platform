"""
Financial Statements Repository Module.

Manages data access and upserting for top-level financial statement headers
(defining company ISIN, filing type, period type, price unit, and data source) in PostgreSQL.
"""

from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement
from core.enum.financial_periods_enum import StatementPeriodTypes
from core.enum.financial_statement_type_enum import FinancialStatmentType
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialStatementRepository(BasePostgresRepository[FinancialStatement]):
    """
    PostgreSQL repository for `FinancialStatement` header records.

    Attributes:
        _model (type[FinancialStatement]): Bound SQLAlchemy model class `FinancialStatement`.
    """

    _model = FinancialStatement

    def __init__(self, session: Session):
        """
        Initialize FinancialStatementRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(
        self,
        finance_data_source_id: int,
        isin: str,
        financial_report_price_unit_id: int,
        finance_statement_type: FinancialStatmentType,
        financial_statement_period_type: StatementPeriodTypes
    ) -> int:
        """
        Upsert a financial statement header and return its primary key ID.

        Identifies a unique statement header by composite key:
        (finance_data_source_id, isin, financial_report_price_unit_id, finance_statement_type, financial_statement_period_type).

        Parameters:
            finance_data_source_id (int): Foreign key to `finance_data_source`.
            isin (str): 12-character International Securities Identification Number.
            financial_report_price_unit_id (int): Foreign key to `financial_report_price_units`.
            finance_statement_type (FinancialStatmentType): Statement type ('consolidated' vs 'standalone').
            financial_statement_period_type (StatementPeriodTypes): Period frequency (yearly, quarterly, etc.).

        Returns:
            int: Primary key ID of the financial statement record.
        """
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

        result = super()._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result
