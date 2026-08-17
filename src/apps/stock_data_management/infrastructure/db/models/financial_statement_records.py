from apps.stock_data_management.infrastructure.db.models.financial_period_types import FinancialPeriodTypes
from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement
from core.models.base import PostgresBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint


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

    finance_period_type_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_period_types.finance_period_type_id"
        ),
        index=True,
        nullable=False,
    )
    
    finance_period: Mapped["FinancialPeriodTypes"] = relationship(
        "FinancialPeriodTypes",
    )
    
    finance_statement: Mapped["FinancialStatement"] = relationship(
            "FinancialStatement",
            back_populates="finance_statement_record"
    )

    __table_args__ = (
        UniqueConstraint(
            financial_statement_id, finance_period_type_id, name="unq_financial_statement_record"
        ),
    )
