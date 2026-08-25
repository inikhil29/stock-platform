"""
Company Profile Repository Module.

Manages data access for corporate summary metadata, business descriptions,
and industry sectors in PostgreSQL.
"""

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.company_profile import CompanyProfile
from core.repositories.base_postgres_repository import BasePostgresRepository


class CompanyProfileRepository(BasePostgresRepository[CompanyProfile]):
    """
    PostgreSQL repository for querying and managing `CompanyProfile` records.

    Attributes:
        _model (type[CompanyProfile]): Bound SQLAlchemy model class `CompanyProfile`.
    """

    _model = CompanyProfile

    def __init__(self, session: Session):
        """
        Initialize CompanyProfileRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def check_if_record_exist(self, isin: str) -> bool:
        """
        Check whether a company profile record exists for the given ISIN.

        Parameters:
            isin (str): 12-character International Securities Identification Number.

        Returns:
            bool: True if profile exists, False otherwise.
        """
        stmt = select(
            exists().where(
                self._model.isin == isin
            )
        )
        res = self._session.scalar(stmt)
        return bool(res)
