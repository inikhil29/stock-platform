from sqlalchemy import ForeignKey

from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped


class FinancialStatement(PostgresBase):
    __tablename__ = 'financial_statement'
    
    financial_statement_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    finance_datat_source_id: Mapped[int] = mapped_column(
        ForeignKey(
            "finace_data_source.finance_data_source_id"
        ),
        index=True,
        nullable=False,
    )
    isin: Mapped[str] = mapped_column(
        ForeignKey(
            
        )
    )