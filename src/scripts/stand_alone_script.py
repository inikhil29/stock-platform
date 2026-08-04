import requests

from apps.stock_info.infrastructure.clients.upstox_client import UpstoxClient


upstox_client = UpstoxClient()
access_token = upstox_client.get_valid_token()
url = 'https://api.stock_info.com/v2/fundamentals/INE0KCE01017/balance-sheet'

params = {
    'type': 'consolidated',
    'fs': 'true'
}
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, params=params, headers=headers)
print(response.json())