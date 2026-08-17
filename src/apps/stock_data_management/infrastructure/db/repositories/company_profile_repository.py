from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.company_profile import CompanyProfile
from core.repositories.base_postgres_repository import BasePostgresRepository


class CompanyProfileRepository(
    BasePostgresRepository[CompanyProfile]
):
    _model = CompanyProfile

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def check_if_record_exist(self, isin: str) -> bool:
        stmt = select(
            exists().where(
                self._model.isin == isin
            )
        )

        res = self._session.scalar(
            stmt
        )
        return res