from sqlalchemy import select, exists
from apps.stock_data_management.infrastructure.db.models.company_profile import CompanyProfile
from core.repositories.base_postgres_repository import BasePostgresRepository


class CompanyProfileRepository(
    BasePostgresRepository
):

    def __init__(self, session_factory):

        super().__init__(
            session_factory=session_factory
        )
        self.model=CompanyProfile

    def check_if_record_exist(self, isin: str) -> bool:
        stmt = select(
            exists().where(
                self.model.isin == isin
            )
        )
        with self.session_factory() as session:
            res = session.scalar(
                stmt
            )
            return res
        return False
