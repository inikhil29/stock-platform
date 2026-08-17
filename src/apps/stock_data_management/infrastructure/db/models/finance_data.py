from apps.stock_data_management.infrastructure.db.models.finance_metrics import FinanceMetrics
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, UniqueConstraint


class FinanceData(PostgresBase):

    __tablename__ = 'finance_metrics'
    finance_data_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    financial_statement_record_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_statement_record_id"
        ),
        index=True,
        nullable=False,
    )
    finance_metric_id: Mapped[int] = mapped_column(
        ForeignKey(
            "finance_metrics.finance_metric_id"
        ),
        nullable=False,
        index=True,
    )
    value: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    finance_metric_details: Mapped["FinanceMetrics"] = relationship(
        "FinanceMetrics"
    )

    __table_args__ = (
        UniqueConstraint(
            financial_statement_record_id, finance_metric_id, name="unq_finance_record_data"
        ),
    )
