from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.company_profile import CompanyProfile
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData

class CompanyProfieQueries:
    def __init__(self, session:Session):
        self._session = session
        
    def get_missing_companies_stream(self, batch_size: int | None = 1000):
        stmt = select(
            StockInstrumentsData
        ).distinct(StockInstrumentsData.isin).outerjoin(
            CompanyProfile, CompanyProfile.isin == StockInstrumentsData.isin
        ).where(
            StockInstrumentsData.isin.isnot(None),
            StockInstrumentsData.isin != '',
            CompanyProfile.isin.is_(None)
        )
        
        result = self._session.scalars(
            stmt.execution_options(
                yield_per=batch_size
            )
        )
        
        for row in result:
            yield row