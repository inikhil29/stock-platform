from sqlalchemy import Integer, String, UniqueConstraint

from core.models.base import PostgresBase

from sqlalchemy.orm import Mapped, mapped_column


class FinancialReportPriceUnits(PostgresBase):
    
    
    __tablename__ = 'financial_report_price_units'
    
    financial_report_price_unit_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    
    units: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )
    
    in_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True
    )
    
    
    __table_args__ = (
        UniqueConstraint(
           'units', 'in_number', name='unq_price_units' 
        )
    )
    