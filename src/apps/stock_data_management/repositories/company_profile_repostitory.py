from sqlalchemy import select, exists
from core.repositories.base_postgres_repository import BasePostgresRepository


class CompanyProfileRepository(
    BasePostgresRepository
):

    def __init__(self, session_factory, model):

        super().__init__(
            model=model,
            session_factory=session_factory
        )

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
