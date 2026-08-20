from datetime import datetime
from sqlalchemy import TIMESTAMP, Enum as SQLEnum, func

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
        ),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
