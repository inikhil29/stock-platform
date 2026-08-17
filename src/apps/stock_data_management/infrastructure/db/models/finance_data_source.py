from sqlalchemy import Enum as SQLEnum

from core.enum.financial_data_source_enum import FinancialDataSourceEnum
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped


class FinanceDataSource(PostgresBase):

    __tablename__ = 'finace_data_source'

    finance_data_source_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    source_name: Mapped[FinancialDataSourceEnum] = mapped_column(
        SQLEnum(
            FinancialDataSourceEnum,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False,
        unique=True,
    )
