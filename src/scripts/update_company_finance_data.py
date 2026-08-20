from apps.stock_data_management.container import (
    StockDataManagementContainer
)
isin = 'INE958A01011'
container = StockDataManagementContainer()
finance_data_service = container.get_company_financial_data_service()
finance_data_service.parse_balance_sheet_from_upstox(
    isin
)
finance_data_service.parse_cash_flow_data_from_upstox(
    isin
)
finance_data_service.parse_income_statement_data_from_upstox(
    isin
)