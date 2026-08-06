from datetime import date

from core.models.base import PostgresBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, Enum as SQLEnum, Date

from core.enum.financial_periods import FinancialPeriod
from core.enum.financial_quarter import FinancialQuarter



class FinancialPeriodType(PostgresBase):
    __tablename__ = 'financial_period_type'
    
    financial_period_type_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,    
    )
    financial_period_type:Mapped[FinancialPeriod] = mapped_column(
        SQLEnum(
            FinancialPeriod,
            values_callable= lambda enum: [e.value for e in enum]
        ),
        nullable=False
    )
    quarter:Mapped[FinancialQuarter] = mapped_column(
        SQLEnum(
            FinancialQuarter,
            value_callable= lambda enum: [e.value for e in enum]
        ),
        nullable=True
    )
    end_date:Mapped[date] = mapped_column(
        Date, 
        nullable=False
    )
    
    __table_args__=(
        CheckConstraint(
            "financial_period_type != 'q' OR quarter IS NOT NULL",
            name="chk_quarter_is_required"
        ),
    )