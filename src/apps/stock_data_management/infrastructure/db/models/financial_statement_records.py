from datetime import datetime
from typing import TYPE_CHECKING


from core.models.base import PostgresBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import TIMESTAMP, Float, ForeignKey, Integer, String, UniqueConstraint, func

if TYPE_CHECKING:
    from apps.stock_data_management.infrastructure.db.models.finance_metrics import FinanceMetrics
    from apps.stock_data_management.infrastructure.db.models.financial_period_types import FinancialPeriodTypes
    from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement


class FinancialStatementRecords(PostgresBase):
    __tablename__ = 'financial_statement_records'

    financial_statement_record_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    financial_statement_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_statements.financial_statement_id"
        ),
        index=True,
        nullable=False,
    )

    financial_period_type_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_period_types.financial_period_type_id"
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
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    finance_period: Mapped["FinancialPeriodTypes"] = relationship(
        "FinancialPeriodTypes",
    )

    finance_statement: Mapped["FinancialStatement"] = relationship(
        "FinancialStatement",
        back_populates="finance_statement_record"
    )

    finance_metric_details: Mapped["FinanceMetrics"] = relationship(
        "FinanceMetrics"
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

    __table_args__ = (
        UniqueConstraint(
            financial_statement_id, financial_period_type_id, finance_metric_id, name="unq_financial_statement_record"
        ),
    )
