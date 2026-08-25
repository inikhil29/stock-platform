"""
Finance Data Source Repository Module.

Manages data access for financial statement source providers (e.g. Upstox, NSE) in PostgreSQL.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.finance_data_source import FinanceDataSource
from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinanceDataSourceRepository(BasePostgresRepository[FinanceDataSource]):
    """
    PostgreSQL repository for `FinanceDataSource` records.

    Attributes:
        _model (type[FinanceDataSource]): Bound SQLAlchemy model class `FinanceDataSource`.
    """

    _model = FinanceDataSource

    def __init__(self, session: Session):
        """
        Initialize FinanceDataSourceRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(self, source_name: FinancialDataSourceEnum) -> int:
        """
        Upsert a data source record by enum name and return its primary key ID.

        Parameters:
            source_name (FinancialDataSourceEnum): Data provider enum (e.g. FinancialDataSourceEnum.UPSTOX).

        Returns:
            int: Primary key ID of the data source record.
        """
        insert_data = {
            self._model.source_name: source_name,
        }

        unique_columns = [
            self._model.source_name,
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
