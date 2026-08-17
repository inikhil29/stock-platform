from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.finance_data_source import FinanceDataSource
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinanceDataSourceRepository(
    BasePostgresRepository[FinanceDataSource]
):
    _model = FinanceDataSource

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )