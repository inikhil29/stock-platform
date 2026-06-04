from apps.nse.infrastructure.clients.nse_client import NseClient
from apps.nse.infrastructure.clients.nse_stock_client import NseStockClient

nse_client = NseClient()
client = NseStockClient(nse_client)
market_data =  client.get_market_status()
print(market_data)