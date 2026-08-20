from datetime import datetime

from core.enum.finance_metrics_enum import FinancialMetric
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TIMESTAMP, String, UniqueConstraint, Enum as SQLEnum, func


class FinanceMetrics(PostgresBase):

    __tablename__ = 'finance_metrics'
    finance_metric_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    metric_code: Mapped[FinancialMetric] = mapped_column(
        SQLEnum(FinancialMetric),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
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