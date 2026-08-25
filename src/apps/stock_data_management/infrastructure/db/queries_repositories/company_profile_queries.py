"""
Company Profile Queries Repository Module.

Provides complex cross-table queries for identifying instruments lacking profile information in PostgreSQL.
"""

from typing import Generator
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.company_profile import CompanyProfile
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData


class CompanyProfieQueries:
    """
    Specialized query repository for company profile coverage and gap analysis.

    Attributes:
        _session (Session): Active SQLAlchemy database session.
    """

    def __init__(self, session: Session):
        """
        Initialize CompanyProfieQueries with an active database session.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        self._session = session

    def get_missing_companies_stream(
        self,
        batch_size: int | None = 1000
    ) -> Generator[StockInstrumentsData, None, None]:
        """
        Stream distinct company instruments that have a non-empty ISIN but do not yet have a record in `company_profile`.

        Performs a DISTINCT ON (`isin`) query with an `OUTER JOIN` onto `company_profile`,
        filtering where `company_profile.isin IS NULL`.

        Parameters:
            batch_size (int | None, optional): Server-side cursor batch size for streaming. Defaults to 1000.

        Yields:
            StockInstrumentsData: Instrument model instance missing profile data.
        """
        stmt = (
            select(StockInstrumentsData)
            .distinct(StockInstrumentsData.isin)
            .outerjoin(
                CompanyProfile,
                CompanyProfile.isin == StockInstrumentsData.isin
            )
            .where(
                StockInstrumentsData.isin.isnot(None),
                StockInstrumentsData.isin != '',
                CompanyProfile.isin.is_(None)
            )
        )

        result = self._session.scalars(
            stmt.execution_options(yield_per=batch_size)
        )

        for row in result:
            yield row
