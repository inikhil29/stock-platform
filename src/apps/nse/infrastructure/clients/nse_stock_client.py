from apps.nse.infrastructure.clients.nse_client import (
    NseClient
)


class NseStockClient:

    def __init__(
        self,
        nse_client: NseClient
    ):

        self._upstox_client = (
            nse_client
        )

        self._http = (
            nse_client.get_http_client()
        )
        

    def get_market_status(
        self,
    ):
        endpoint = f"/api/marketStatus"
        headers = {
            "Accept": "application/json",
        }
        response = self._http.get_json(
            endpoint,
            headers=headers,
        )
        return response
