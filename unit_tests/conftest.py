"""
Global pytest fixtures and mock environments for unit tests.
"""

import os
from unittest.mock import MagicMock
import pytest

# Ensure default environment variables are set before any settings load
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PROTOCOL", "redis")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_NAMESPACE", "test")
os.environ.setdefault("AWS_ACCESS_KEY", "test_key")
os.environ.setdefault("AWS_SECRET_KEY", "test_secret")
os.environ.setdefault("AWS_REGION", "ap-south-1")
os.environ.setdefault("AWS_HISTORICAL_DATA_S3_BUCKET", "test-bucket")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_pass")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "test_db")


@pytest.fixture
def mock_db_session():
    """Create a mock SQLAlchemy Session."""
    session = MagicMock()
    session.execute.return_value = MagicMock()
    session.scalar.return_value = None
    session.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
    return session


@pytest.fixture
def mock_unit_of_work(mock_db_session):
    """Create a mock PostgresUnitOfWork context manager."""
    uow = MagicMock()
    uow._session = mock_db_session
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    
    # Mock repositories on UoW
    uow.stock_instruments_repository = MagicMock()
    uow.company_profiles_repository = MagicMock()
    uow.raw_historical_data_info_repository = MagicMock()
    uow.stock_candle_data_repository = MagicMock()
    uow.finance_metrics_repository = MagicMock()
    uow.finace_data_source_repository = MagicMock()
    uow.financial_period_types_repository = MagicMock()
    uow.financial_report_price_units_repository = MagicMock()
    uow.financial_statement_records_repository = MagicMock()
    uow.financial_statements_repository = MagicMock()
    uow.company_profile_queries_repository = MagicMock()
    
    return uow


@pytest.fixture
def mock_redis_client():
    """Create a mock RedisClient."""
    client = MagicMock()
    client.get.return_value = None
    client.set.return_value = True
    client.set_if_not_exists.return_value = True
    client.ttl.return_value = 3600
    return client


@pytest.fixture
def mock_upstox_client():
    """Create a mock UpstoxClient."""
    client = MagicMock()
    client.get.return_value = {"status": "success", "data": {}}
    client.post.return_value = {"status": "success", "data": {}}
    return client


@pytest.fixture
def mock_aws_client():
    """Create a mock AWS S3 Client."""
    client = MagicMock()
    client.upload_json_to_s3.return_value = True
    client.read_json_from_s3.return_value = {"status": "success", "data": {"candles": []}}
    return client


@pytest.fixture
def sample_instruments():
    """Return a list of sample stock instrument dictionaries."""
    return [
        {
            "instrument_key": "NSE_EQ|INE002A01018",
            "exchange_token": "2885",
            "tradingsymbol": "RELIANCE",
            "name": "RELIANCE INDUSTRIES LTD",
            "last_price": 2900.5,
            "expiry": None,
            "strike": None,
            "tick_size": 0.05,
            "lot_size": 1,
            "instrument_type": "EQUITY",
            "isin": "INE002A01018",
            "exchange": "NSE"
        },
        {
            "instrument_key": "NSE_EQ|INE009A01021",
            "exchange_token": "1594",
            "tradingsymbol": "INFY",
            "name": "INFOSYS LIMITED",
            "last_price": 1600.0,
            "expiry": None,
            "strike": None,
            "tick_size": 0.05,
            "lot_size": 1,
            "instrument_type": "EQUITY",
            "isin": "INE009A01021",
            "exchange": "NSE"
        }
    ]


@pytest.fixture
def sample_candles_response():
    """Return sample Upstox candle response payload."""
    return {
        "status": "success",
        "data": {
            "candles": [
                ["2024-01-01T09:15:00+05:30", 2500.0, 2520.0, 2490.0, 2510.0, 100000, 50000],
                ["2024-01-01T09:16:00+05:30", 2510.0, 2515.0, 2505.0, 2512.0, 45000, 50200]
            ]
        }
    }

