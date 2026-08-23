
from datetime import datetime
from decimal import Decimal

from sqlalchemy import TIMESTAMP, BigInteger, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped

from core.models.base import PostgresBase


class StockCandleData(PostgresBase):

    __tablename__ = "stock_candle_data"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    raw_historical_data_info_id: Mapped[int] = mapped_column(
        ForeignKey(
            "raw_historical_data_info.id"
        ),
        nullable=False,
        index=True
    )

    candle_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    open: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )

    high: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )

    low: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )

    close: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    open_interest: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
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

    __table_args__ = (
        UniqueConstraint(
            "raw_historical_data_info_id",
            "candle_timestamp",
            name="uq_stock_candle_data_time",
        ),
    )
