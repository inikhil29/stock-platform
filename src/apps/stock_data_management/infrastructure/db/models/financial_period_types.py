from datetime import date

from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement
from core.models.base import PostgresBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, Enum as SQLEnum, Date, UniqueConstraint

from core.enum.financial_periods_enum import FinancialPeriod
from core.enum.financial_quarter_enum import FinancialQuarter


class FinancialPeriodTypes(PostgresBase):
    __tablename__ = 'financial_period_types'

    financial_period_type_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    financial_period_type: Mapped[FinancialPeriod] = mapped_column(
        SQLEnum(
            FinancialPeriod,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False
    )
    quarter: Mapped[FinancialQuarter] = mapped_column(
        SQLEnum(
            FinancialQuarter,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=True
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "financial_period_type != 'q' OR quarter IS NOT NULL",
            name="chk_quarter_is_required"
        ),
        UniqueConstraint(
            financial_period_type, end_date, name="unq_period_type_check"
        )
    )
