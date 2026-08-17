from core.models.base import PostgresBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from sqlalchemy import TIMESTAMP, Enum as SQLEnum, func, Date, ForeignKey, UniqueConstraint

from core.enum.candle_interval_enum import CandleInterval

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData


class RawHistoricalDataInfo(PostgresBase):
    __tablename__ = "raw_historical_data_info"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    instrument_key: Mapped[str] = mapped_column(ForeignKey(
        "stock_instruments_data.instrument_key"), index=True, nullable=False)

    interval: Mapped[CandleInterval] = mapped_column(
        SQLEnum(
            CandleInterval,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    from_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    to_date: Mapped[date] = mapped_column(
        Date, nullable=False
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

    instrument: Mapped["StockInstrumentsData"] = relationship(
        "StockInstrumentsData",
        back_populates="historical_data"
    )

    __table_args__ = (
        UniqueConstraint(
            "instrument_key",
            "interval",
            "from_date",
            "to_date",
            name="uq_raw_historical_data_record"
        ),
    )
