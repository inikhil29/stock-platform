from apps.upstox.infrastructure.clients.upstox_client import (
    UpstoxClient
)


class UpstoxInstrumentsClient:

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

    def get_instrument_profile(
        self,
        isin: str
    ):

        access_token = (
            self._upstox_client
            .get_valid_token()
        )
        endpoint = f"/fundamentals/{isin}/profile"
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
