import json
import ijson
from sqlalchemy.dialects.postgresql import insert
from core.infrastructure.database.sql_database.db_context import get_upstox_db
from apps.stock_data_management.infrastructure.db.models.stock_instruments_data import StockInstrumentsData
import requests
import os
from pathlib import Path
import gzip
import shutil
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent


def download_file(url, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_name = url.split("/")[-1]

    file_path = os.path.join(folder_name, file_name)

    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check for HTTP errors
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


def extractFile(file_path, extract_file_path):
    with gzip.open(file_path, "rb") as f_in:
        with open(extract_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            return True

    return False


def download_and_extract_stock_data_file_from_upstox(complete_instruments_download_url, downlaod_dir):
    zip_file_name = complete_instruments_download_url.split("/")[-1]
    zip_file_path = downlaod_dir / zip_file_name
    extract_file_name = ".".join(zip_file_name.split(".")[:-1])
    extract_file_path = downlaod_dir / extract_file_name

    if zip_file_path.exists():
        zip_file_path.unlink()

    if extract_file_path.exists():
        extract_file_path.unlink()

    download_file(complete_instruments_download_url, downlaod_dir)

    if zip_file_path.exists():
        if extractFile(zip_file_path, extract_file_path):
            zip_file_path.unlink()

    return extract_file_path
        
        
def compare_and_update(json_file_path, table):

    valid_columns = {
        col.name
        for col in table.__table__.columns
        if col.name != "id"
    }
    BATCH_SIZE = 1000
    batch = []

    with open(json_file_path, "rb") as json_file:

        # assumes JSON array
        records = ijson.items(json_file, "item")
        for row_number, row in enumerate(records, start=1):

            try:

                # keep only matching columns
                filtered_row = {
                    k: v
                    for k, v in row.items()
                    if k in valid_columns
                }
                # skip empty rows
                if not filtered_row:
                    continue
                
                filtered_row = pd.Series(filtered_row).astype(object)
                filtered_row = filtered_row.reindex(valid_columns)
                filtered_row = filtered_row.where(pd.notnull(filtered_row), None)
                filtered_row = filtered_row.to_dict()

                batch.append(filtered_row)

                if len(batch) >= BATCH_SIZE:
                    process_batch(batch, table)
                    batch.clear()

            except Exception as e:
                print(f"Error processing row {row_number}: {e}")
                return

        # remaining rows
        if batch:
            process_batch(batch, table)


    

def process_batch(batch, table):

    compare_data_change(batch)

    update_records(batch, table)


def compare_data_change(batch):
    print(f"Processing for batch: {batch}")
    print(f"Processing batch size: {len(batch)}")

def update_records(data, table):

    if not data:
        return

    stmt = insert(table).values(data)

    update_dict = {
        c.name: stmt.inserted[c.name]
        for c in table.__table__.columns
        if c.name != "id"
    }

    stmt = stmt.on_duplicate_key_update(**update_dict)

    try:
        with get_upstox_db() as db:

            result = db.execute(stmt)

            db.commit()

            print(f"Inserted/Updated: {result.rowcount}")

    except Exception as e:
        print(f"DB Error: {e}")
        raise


if __name__ == "__main__":
    try:
        complete_instruments_download_url = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
        downlaod_dir = BASE_DIR.parent / "data/instrument_data_from_upstox"
        downlaod_dir.mkdir(parents=True, exist_ok=True)

        extract_file_path = download_and_extract_stock_data_file_from_upstox(
            complete_instruments_download_url, downlaod_dir)
        

        compare_and_update(extract_file_path, StockInstrumentsData)
    except Exception as e:
        pass
