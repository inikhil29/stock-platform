from sqlalchemy import func, select, exists
from sqlalchemy.orm import Session
from apps.stock_data_management.infrastructure.db.models.financial_report_price_units import FinancialReportPriceUnits
from core.enum.price_unit_enum import PriceUnitEnum
from core.repositories.base_postgres_repository import BasePostgresRepository


class FinancialReportPriceUnitsRepository(
    BasePostgresRepository[FinancialReportPriceUnits]
):
    _model = FinancialReportPriceUnits

    def __init__(self, session: Session):

        super().__init__(
            session=session
        )

    def upsert_and_get_id(self, financial_report_price_unit: PriceUnitEnum) -> int:
        insert_data = {
            self._model.units: financial_report_price_unit,
        }

        unique_columns = [
            self._model.units,
        ]

        update_data = {
            self._model.updated_at: func.now()
        }

        result = super()._upsert_and_get_id(insert_data=insert_data,
                                            update_data=update_data, unique_columns=unique_columns)
        return result
