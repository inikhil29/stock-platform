from datetime import date, datetime
from typing import TYPE_CHECKING

from core.models.base import PostgresBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, CheckConstraint, Enum as SQLEnum, Date, UniqueConstraint, func

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
        CheckConstraint(
            "financial_period_type != 'q' OR quarter IS NOT NULL",
            name="chk_quarter_is_required"
        ),
        UniqueConstraint(
            financial_period_type, end_date, name="unq_period_type_check"
        ),
    )
