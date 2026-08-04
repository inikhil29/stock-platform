from sqlalchemy import String

from core.models.base import PostgresBase

from sqlalchemy.orm import mapped_column, Mapped

class FinanceDataSource(PostgresBase):
    
    
    __tablename__ = 'finace_data_source'
    
    finance_data_source_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    
    source_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )