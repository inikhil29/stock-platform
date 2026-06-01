from pathlib import Path

from core.clients.file_client import(
    FileClient
)


from core.utilities.file_utilities import (
    extract_gzip_file
)

from apps.upstox.container import (
    UpstoxContainer
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
    client = FileClient()

    client.download_file(
        DOWNLOAD_URL,
        gzip_path
    )
    
    upstox_instrument_container = UpstoxContainer()
    upstox_instrument_service = upstox_instrument_container.get_upstox_instrument_service()

    # -----------------------------
    # EXTRACT
    # -----------------------------
    extract_gzip_file(
        gzip_path,
        json_path
    )

    
    upstox_instrument_service.sync_instruments(
        json_path
    )


if __name__ == "__main__":

    main()