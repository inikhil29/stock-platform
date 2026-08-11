from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import PostgresBase
from apps.stock_data_management.infrastructure.db.models.raw_historical_data_info import RawHistoricalDataInfo


class StockInstrumentsData(PostgresBase):
    __tablename__ = "stock_instruments_data"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    exchange: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    isin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    instrument_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    instrument_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    trading_symbol: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    segment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    historical_data: Mapped[list["RawHistoricalDataInfo"]] = relationship(
        "RawHistoricalDataInfo",
        back_populates="instrument",
        cascade="all, delete-orphan",
    )
