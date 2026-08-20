from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Integer, String, UniqueConstraint, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enum.price_unit_enum import PriceUnitEnum
from core.models.base import PostgresBase

if TYPE_CHECKING:
    from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement


class FinancialReportPriceUnits(PostgresBase):

    __tablename__ = 'financial_report_price_units'

    financial_report_price_unit_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    units: Mapped[PriceUnitEnum] = mapped_column(
        SQLEnum(
            PriceUnitEnum,
        ),
        nullable=False,
        unique=True
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

    finance_statement_data: Mapped[list["FinancialStatement"]] = relationship(
        "FinancialStatement",
        back_populates="finance_price_unit_in"
    )
