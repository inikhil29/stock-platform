from sqlalchemy import Column, Integer, String, Text
from core.models.base import Base


class UpstoxStockInstrumentData(Base):
    __tablename__ = "upstox_stock_instrument_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(255), nullable=False, index=True)
    isin = Column(String(255), nullable=True, index=True)
    instrument_type = Column(String(255), nullable=False, index=True)
    instrument_key = Column(String(255), nullable=False, unique=True, index=True)
    trading_symbol = Column(String(255), nullable=False)
    segment = Column(String(50), nullable=False, index=True)
    sector = Column(String(50), nullable=True, index=True)
    company_profile = Column(Text, nullable=True, index=False)