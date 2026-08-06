from pathlib import Path

from core.clients.file_client import(
    FileClient
)


from core.utilities.file_utilities import (
    extract_gzip_file
)

from apps.stock_data_management.container import (
    StockDataManagementContainer
)

BASE_DIR = (
    Path(__file__).resolve().parent
)


DOWNLOAD_URL = (
    "https://assets.upstox.com/"
    "market-quote/instruments/"
    "exchange/complete.json.gz"
)


def main():

    data_dir = (
        BASE_DIR.parent
        / "data"
        / "instrument_data"
    )

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    gzip_path = (
        data_dir
        / "complete.json.gz"
    )

    json_path = (
        data_dir
        / "complete.json"
    )

    # -----------------------------
    # DOWNLOAD
    # -----------------------------
    file_client = FileClient()

    file_client.download_file(
        DOWNLOAD_URL,
        gzip_path
    )
    
    stock_data_management_container = StockDataManagementContainer()
    stock_instrument_service = stock_data_management_container.get_stock_instrument_service()

    # -----------------------------
    # EXTRACT
    # -----------------------------
    extract_gzip_file(
        gzip_path,
        json_path
    )

    
    stock_instrument_service.sync_instruments_new(
        json_path
    )
    
    gzip_path.unlink(missing_ok=True)
    json_path.unlink(missing_ok=True)

if __name__ == "__main__":

    main()