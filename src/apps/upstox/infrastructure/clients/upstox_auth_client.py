

from urllib.parse import urlencode
import requests

from apps.upstox.config import settings
from apps.upstox.config.upstox_apis import upstox_apis
from core.cache.redis_client import RedisClient
from core.clients.http_client import HttpClient


class UpstoxAuthClient:
    def __init__(self, client_id, client_secret, redirect_uri, httpClient:HttpClient, cache:RedisClient = None):

        self.http = httpClient        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def __start_authorizing_process(self):
        upstox_base_url = settings.UPSTOX_LIVE_URL
        authorization_endpoint = upstox_apis.AUTHORIZE_API
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
        }
        
        auth_url = f"{upstox_base_url}{authorization_endpoint}?{urlencode(params)}"
        print(f"Use this url to get the code: {auth_url}")
        authorization_code = input("Enter the authorizing code: ")
        if authorization_code and authorization_code != '':
            return authorization_code
        else:
            raise Exception(
                'Invalid Authrization code given, Please provide a valid code.')

    def refresh_token(self):
        
        authorize_code = self.__start_authorizing_process()
        access_token_endpoint = upstox_apis.ACCESS_TOKEN_API
        access_token_result = self._fetch_access_token(access_token_endpoint, authorize_code)
        return access_token_result
        

    def _fetch_access_token(self, access_token_endpoint,  authorize_code: str):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'code': authorize_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }

        try:
            response = self.http.postHttpRequest(
                access_token_endpoint, data=data, headers=headers)
            return response
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            raise