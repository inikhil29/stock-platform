from apps.stock_data_management.infrastructure.clients.upstox_client import (
    UpstoxClient
)


class CompanyFinancialDataClient:

    def __init__(
        self,
        upstox_client: UpstoxClient
    ):

        self._upstox_client = (
            upstox_client
        )

        self._http = (
            upstox_client.get_http_client()
        )

    def get_balance_sheet_from_upstox(
        self,
        isin: str,
        type: str = 'consolidated',
        fs: bool = True,
    ):

        access_token = (
            self._upstox_client
            .get_valid_token()
        )
        endpoint = f"/v2/fundamentals/{isin}/balance-sheet"
        headers = {
            "Accept": "application/json",
            "Authorization":
            f"Bearer {access_token}"
        }
        params = {
            'type': type,
            'fs': fs
        }
        response = self._http.get_json(
            endpoint,
            headers=headers,
            params=params
        )
        return response['data']

    def get_cash_flow_from_upstox(
        self,
        isin: str,
        type: str = 'consolidated',
        fs: bool = True,
    ):

        access_token = (
            self._upstox_client
            .get_valid_token()
        )
        endpoint = f"/v2/fundamentals/{isin}/cash-flow"
        headers = {
            "Accept": "application/json",
            "Authorization":
            f"Bearer {access_token}"
        }
        params = {
            'type': type,
            'fs': fs
        }
        response = self._http.get_json(
            endpoint,
            headers=headers,
            params=params
        )
        return response['data']

    def get_income_statement_from_upstox(
        self,
        isin: str,
        type: str = 'consolidated',
        time_period: str = 'quarterly',
        fs: bool = True,
    ):

        access_token = (
            self._upstox_client
            .get_valid_token()
        )
        endpoint = f"/v2/fundamentals/{isin}/income-statement"
        headers = {
            "Accept": "application/json",
            "Authorization":
            f"Bearer {access_token}"
        }
        params = {
            'type': type,
            'time_period': time_period,
            'fs': fs,
        }
        response = self._http.get_json(
            endpoint,
            headers=headers,
            params=params
        )
        return response['data']
