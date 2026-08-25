from core.enum.finance_metrics_enum import FinancialMetric


FINANCIAL_METRIC_ALIASES: dict[str, FinancialMetric] = {
    "Profit before tax": FinancialMetric.PROFIT_BEFORE_TAX,
    "Profit Before Tax": FinancialMetric.PROFIT_BEFORE_TAX,
    "Income before WC changes": FinancialMetric.INCOME_BEFORE_WC_CHANGES,
    "Change in Assets": FinancialMetric.CHANGE_IN_ASSETS,
    "Change in Liabilities": FinancialMetric.CHANGE_IN_LIABILITIES,
    "Change in WC": FinancialMetric.CHANGE_IN_WC,
    "Cash flow from Operations": FinancialMetric.CASH_FLOW_FROM_OPERATIONS,
    "Cash flow from Investing": FinancialMetric.CASH_FLOW_FROM_INVESTING,
    "Cash flow from Financing": FinancialMetric.CASH_FLOW_FROM_FINANCING,
    "Total Cash Flow": FinancialMetric.TOTAL_CASH_FLOW,
    "Cash (Start of the year)": FinancialMetric.CASH_START_OF_YEAR,
    "Cash (End of the year)": FinancialMetric.CASH_END_OF_YEAR,

    "operating": FinancialMetric.OPERATING,
    "investing": FinancialMetric.INVESTING,
    "financing": FinancialMetric.FINANCING,

    "Non-Current Assets": FinancialMetric.NON_CURRENT_ASSETS,
    "Current Assets": FinancialMetric.CURRENT_ASSETS,
    "Total Assets": FinancialMetric.TOTAL_ASSETS,
    "Current Liabilities": FinancialMetric.CURRENT_LIABILITIES,
    "Net Current Asset": FinancialMetric.NET_CURRENT_ASSET,
    "Non-Current Liabilities": FinancialMetric.NON_CURRENT_LIABILITIES,
    "Equity Capital": FinancialMetric.EQUITY_CAPITAL,
    "Total Equity & Liabilities": FinancialMetric.TOTAL_EQUITY_LIABILITIES,

    "revenue": FinancialMetric.REVENUE,
    "Revenue": FinancialMetric.REVENUE,
    "operating_profit": FinancialMetric.OPERATING_PROFIT,
    "net_profit": FinancialMetric.NET_PROFIT,

    "Other Income": FinancialMetric.OTHER_INCOME,
    "Total Revenue": FinancialMetric.TOTAL_REVENUE,
    "Total Expenses": FinancialMetric.TOTAL_EXPENSES,
    "Tax": FinancialMetric.TAX,
    "Profit After Tax": FinancialMetric.PROFIT_AFTER_TAX,
    "EPS - Basic": FinancialMetric.EPS_BASIC,
    "EPS - Diluted": FinancialMetric.EPS_DILUTED,
}
