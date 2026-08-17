from sqlalchemy.orm import sessionmaker, Session

from apps.stock_data_management.infrastructure.db.queries_repositories.company_profile_queries import CompanyProfieQueries
from apps.stock_data_management.infrastructure.db.repositories.company_profile_repository import (
    CompanyProfileRepository,
)
from apps.stock_data_management.infrastructure.db.repositories.raw_historical_data_info_repository import (
    StockRawHistoricalDataInfoRepository,
)
from apps.stock_data_management.infrastructure.db.repositories.stock_instruments_repository import (
    StockInstrumentsRepository,
)

class PostgresUnitOfWork:

    def __init__(self, session_factory:sessionmaker[Session]):
        self._session_factory = session_factory

    def __enter__(self):
        self._session = self._session_factory()

        self.stock_instruments_repository = StockInstrumentsRepository(
            self._session
        )

        self.company_profiles_repository = CompanyProfileRepository(
            self._session
        )

        self.raw_historical_data_info_repository = (
            StockRawHistoricalDataInfoRepository(
                self._session
            )
        )
        
        self.company_profile_queries_repository = (
            CompanyProfieQueries(
                self._session
            )
        )
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            self._session.close()
            self._session = None

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
