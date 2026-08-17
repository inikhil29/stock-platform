from sqlalchemy import ForeignKey, Enum as SQLEnum, UniqueConstraint

from apps.stock_data_management.infrastructure.db.models.financial_report_price_units import FinancialReportPriceUnits
from apps.stock_data_management.infrastructure.db.models.financial_statement_records import FinancialStatementRecords
from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped, relationship
from core.enum.financial_statement_type_enum import FinancialStatmentType


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
            finance_data_source_id, isin, financial_report_price_unit_id, finance_statement_type, name="unq_financial_statement"
        ),
    )
