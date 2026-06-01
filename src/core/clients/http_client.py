import requests


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def getHttpRequest(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(
                url, **kwargs
            )

        response.raise_for_status()
        return response.json()

    def postHttpRequest(self, endpoint, data=None, json=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(
                url,
                data=data,
                json=json,
                **kwargs
            )
        response.raise_for_status()
        return response.json()
    
    @classmethod
    def get(cls, url, stream=False):
        response =  requests.get(url=url, stream=stream)
        response.raise_for_status()
        return response