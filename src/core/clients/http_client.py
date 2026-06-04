import requests


class HttpClient:
    def __init__(self, base_url):
        self._base_url = base_url
        self._session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self._base_url}{endpoint}"

        response = self._session.request(
            method=method,
            url=url,
            **kwargs
        )

        response.raise_for_status()
        return response

    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def get_json(self, endpoint: str, **kwargs):
        return self.get(endpoint, **kwargs).json()

    def post_json(self, endpoint: str, **kwargs):
        return self.post(endpoint, **kwargs).json()

    @staticmethod
    def download(url: str, stream: bool = False):
        response = requests.get(url, stream=stream)
        response.raise_for_status()
        return response
