from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String


class FinanceMetrics(PostgresBase):
    
    __tablename__ = 'finance_metrics'
    finance_metric_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    metric_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    
    display_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )