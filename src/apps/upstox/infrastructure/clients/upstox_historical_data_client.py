from datetime import date

from apps.upstox.infrastructure.clients.upstox_client import (
    UpstoxClient
)


class UpstoxHistoricalDataClient:

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

    def get_historical_data(
        self,
        instrument_key: str,
        unit:str,
        interval_option: int,
        to_date: date,
        from_date: date | None = None
    ):

        access_token = (
            self._upstox_client
            .get_valid_token()
        )
        endpoint = f"/v3/historical-candle/{instrument_key}/{unit}/{interval_option}/{to_date}/{from_date}"
        headers = {
            "Accept": "application/json",
            "Authorization":
            f"Bearer {access_token}"
        }
        response = self._http.get_json(
            endpoint,
            headers=headers,
        )
        return response['data']
