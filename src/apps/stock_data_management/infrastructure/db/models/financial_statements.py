from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Enum as SQLEnum, UniqueConstraint, func

from core.enum.financial_periods_enum import StatementPeriodTypes
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped, relationship
from core.enum.financial_statement_type_enum import FinancialStatmentType

if TYPE_CHECKING:
    from apps.stock_data_management.infrastructure.db.models.financial_report_price_units import FinancialReportPriceUnits
    from apps.stock_data_management.infrastructure.db.models.financial_statement_records import FinancialStatementRecords

class FinancialStatement(PostgresBase):
    __tablename__ = 'financial_statements'

    financial_statement_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    finance_data_source_id: Mapped[int] = mapped_column(
        ForeignKey(
            "finace_data_source.finance_data_source_id"
        ),
        index=True,
        nullable=False,
    )
    isin: Mapped[str] = mapped_column(
        ForeignKey(
            "company_profile.isin"
        ),
        index=True,
        nullable=False,
    )
    financial_report_price_unit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_report_price_units.financial_report_price_unit_id"
        ),
        index=True,
        nullable=False,
    )
    finance_statement_type: Mapped[FinancialStatmentType] = mapped_column(
        SQLEnum(
            FinancialStatmentType,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False
    )
    financial_statement_period_type: Mapped[StatementPeriodTypes] = mapped_column(
        SQLEnum(
            StatementPeriodTypes,
        ),
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

    finance_price_unit_in: Mapped["FinancialReportPriceUnits"] = relationship(
        "FinancialReportPriceUnits",
        back_populates="finance_statement_data"
    )

    finance_statement_record: Mapped[list["FinancialStatementRecords"]] = relationship(
        "FinancialStatementRecords",
        back_populates="finance_statement",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            finance_data_source_id, isin, financial_report_price_unit_id, finance_statement_type, financial_statement_period_type, name="unq_financial_statement"
        ),
    )
