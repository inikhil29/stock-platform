"""
Financial Report Price Units Repository Module.

Manages data access and upserting for financial statement denomination units
(Crores, Lakhs, Thousands, Single Units) in PostgreSQL.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.stock_data_management.infrastructure.db.models.financial_report_price_units import FinancialReportPriceUnits
from core.enum.price_unit_enum import PriceUnitEnum
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialReportPriceUnitsRepository(BasePostgresRepository[FinancialReportPriceUnits]):
    """
    PostgreSQL repository for `FinancialReportPriceUnits` records.

    Attributes:
        _model (type[FinancialReportPriceUnits]): Bound SQLAlchemy model class `FinancialReportPriceUnits`.
    """

    _model = FinancialReportPriceUnits

    def __init__(self, session: Session):
        """
        Initialize FinancialReportPriceUnitsRepository.

        Parameters:
            session (Session): Active SQLAlchemy database session.
        """
        super().__init__(session=session)

    def upsert_and_get_id(self, financial_report_price_unit: PriceUnitEnum) -> int:
        """
        Upsert a price denomination unit enum and return its primary key ID.

        Parameters:
            financial_report_price_unit (PriceUnitEnum): Denomination unit enum (e.g. PriceUnitEnum.CRORES).

        Returns:
            int: Primary key ID of the price unit record.
        """
        insert_data = {
            self._model.units: financial_report_price_unit,
        }

        unique_columns = [
            self._model.units,
        ]

        update_data = {
            self._model.updated_at: func.now()
        }

        result = super()._upsert_and_get_id(
            insert_data=insert_data,
            update_data=update_data,
            unique_columns=unique_columns
        )
        return result
