from core.enum.finance_metrics_enum import FinancialMetric
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, UniqueConstraint, Enum as SQLEnum


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
    
    __table_args__ = (
        UniqueConstraint(
            metric_code, display_name, name="unq_metric_name"
        )
    )