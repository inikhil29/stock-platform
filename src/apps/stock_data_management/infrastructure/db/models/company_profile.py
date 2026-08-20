from datetime import datetime

from core.models.base import PostgresBase
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TIMESTAMP, String, Text, func


class CompanyProfile(PostgresBase):

    __tablename__ = "company_profile"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    isin: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    sector: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    company_profile: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )