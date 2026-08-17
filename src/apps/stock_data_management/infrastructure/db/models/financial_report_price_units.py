from sqlalchemy import Integer, String, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.stock_data_management.infrastructure.db.models.financial_statements import FinancialStatement
from core.enum.price_unit_enum import PriceUnitEnum
from core.models.base import PostgresBase


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

    finance_statement_data: Mapped[list["FinancialStatement"]] = relationship(
        "FinancialStatement",
        back_populates="finance_price_unit_in"
    )
