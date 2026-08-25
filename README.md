# Stock Market Data Management Service

A high-performance, modular data engineering platform designed to extract, transform, archive, and persist Indian stock market (NSE / BSE) metadata, time-series historical candlestick data, corporate company profiles, and financial statements (Balance Sheets, Income Statements, Cash Flow).

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Project Directory Structure](#project-directory-structure)
3. [Service Catalog & Lifecycle Management](#service-catalog--lifecycle-management)
4. [Models & Repositories: Linkages & Usage](#models--repositories-linkages--usage)
5. [Data Pipelines & Workflows](#data-pipelines--workflows)
6. [Polyglot Storage Design](#polyglot-storage-design)
7. [Getting Started & Operations](#getting-started--operations)

---

## Architectural Overview

The service utilizes a **Clean Architecture** layered design with **Polyglot Persistence**, strict **Unit of Work (UoW)** transaction scoping, and an **Inversion of Control (IoC) Container** for dependency management.

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 Upstox Market APIs v2/v3                │
                  └───────────┬──────────────────┬───────────────────┬──────┘
                              │                  │                   │
                              ▼                  ▼                   ▼
                     [UpstoxAuthClient]   [UpstoxClient]   [CompanyFinancialDataClient]
                              │                  │                   │
                              └──────────┬───────┴───────────────────┘
                                         ▼
                   ┌───────────────────────────────────────────┐
                   │       StockDataManagementContainer        │
                   └─────────────────────┬─────────────────────┘
                                         │  (Injects UoW & Clients)
                                         ▼
                   ┌───────────────────────────────────────────┐
                   │             Services Layer                │
                   │  - UpstoxAccessTokenManager               │
                   │  - StockInstrumentsService                │
                   │  - CompanyProfileService                  │
                   │  - StockHistoricalDataService             │
                   │  - CompanyFinanceServices                 │
                   └─────────────────────┬─────────────────────┘
                                         │  (Unit of Work Context)
                                         ▼
                   ┌───────────────────────────────────────────┐
                   │            PostgresUnitOfWork             │
                   │  - Wraps Session Lifecycle (Commit/Roll)  │
                   │  - Injects Session into Repositories      │
                   └─────────────────────┬─────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌────────────────┐             ┌──────────────────┐             ┌────────────────────┐
│   PostgreSQL   │             │     MongoDB      │             │       AWS S3       │
│  (Relational   │             │   (Unstructured  │             │   (Raw Historical  │
│   Analytics)   │             │  Company Profile)│             │   Candle Archives) │
└────────────────┘             └──────────────────┘             └────────────────────┘
```

---

## Project Directory Structure

```
Stock_Data_Service/
├── pyproject.toml                     # Package dependencies, build tools & pytest configuration
├── README.md                          # Platform architecture and technical documentation
└── src/
    ├── alembic/                       # Database schema migration environment
    │   ├── env.py                     # Alembic migration runner with SQLAlchemy metadata
    │   └── versions/                  # Schema migration revision scripts
    ├── apps/
    │   └── stock_data_management/     # Domain Application: Stock Market Data Ingestion
    │       ├── container.py           # IoC Container wiring clients, repositories, and services
    │       ├── config/                # Domain-specific mappings & metric aliases
    │       │   ├── finance_matrics_alias_mapping.py  # Financial line item mapping to enum
    │       │   └── finance_units_alias_mapping.py    # Currency denomination alias mapping
    │       ├── infrastructure/        # External adapters (APIs, DBs, Storage)
    │       │   ├── clients/           # HTTP API client wrappers for Upstox API endpoints
    │       │   │   ├── company_financial_data_client.py  # Fundamental statement client
    │       │   │   ├── stock_historical_data_client.py   # Historical candle v3 client
    │       │   │   ├── stock_instruments_client.py       # Instrument metadata client
    │       │   │   ├── upstox_auth_client.py             # OAuth 2.0 authentication client
    │       │   │   └── upstox_client.py                  # Core authenticated HTTP client
    │       │   ├── db/                # Persistence implementations
    │       │   │   ├── session.py     # SQLAlchemy session factories (Postgres / MySQL)
    │       │   │   ├── mongodb.py     # MongoDB database connection factory
    │       │   │   ├── postgres_unit_of_work.py  # Unit of Work for transactional scoping
    │       │   │   ├── models/        # SQLAlchemy ORM and Pydantic schema models
    │       │   │   │   ├── company_profile.py             # Relational company summary
    │       │   │   │   ├── finance_data_source.py         # Financial data providers
    │       │   │   │   ├── finance_metrics.py             # Line-item metric definitions
    │       │   │   │   ├── financial_period_types.py      # Reporting period boundaries
    │       │   │   │   ├── financial_report_price_units.py # Price units (Crores/Lakhs)
    │       │   │   │   ├── financial_statement_records.py # Financial line-item values
    │       │   │   │   ├── financial_statements.py        # Financial statement headers
    │       │   │   │   ├── instruments_profile.py         # Mongo document schema
    │       │   │   │   ├── raw_historical_data_info.py    # S3 candle ingestion metadata
    │       │   │   │   ├── stock_candle_data.py           # Time-series candle OHLCV
    │       │   │   │   └── stock_instruments_data.py      # Stock/index instruments table
    │       │   │   ├── queries_repositories/  # Specialized analytical and cross-table queries
    │       │   │   │   ├── candle_data_queries.py     # Candle aggregation query repository
    │       │   │   │   └── company_profile_queries.py # Missing profile gap detection
    │       │   │   └── repositories/  # PostgreSQL & MongoDB domain repositories
    │       │   └── store/             # In-memory and cache stores
    │       │       └── upstox_token_store.py  # Redis access token store with TTL
    │       └── services/              # Domain Services orchestrating business logic
    │           ├── company_finance_services.py       # Statement parsing & normalization
    │           ├── company_profile_services.py       # Dual-storage company profile sync
    │           ├── stock_historical_data_service.py  # S3 archiving & candle bulk ingestion
    │           ├── stock_instruments_service.py      # Polars/ijson instrument synchronization
    │           └── upstox_access_token_manager.py    # Thread-safe OAuth token manager
    ├── core/                          # Reusable Core Framework (Database, Cloud, Utilities)
    │   ├── clients/                   # Shared infrastructure clients (AWS S3, HTTP, Redis)
    │   ├── config/                    # Global settings (Pydantic Settings: DB, S3, Redis)
    │   ├── dataframe/                 # DataFrame abstraction engine (Polars reader, writer, schema)
    │   ├── enum/                      # Domain enums (Intervals, Quarters, Units, Statements)
    │   ├── infrastructure/            # Core DB engines (Postgres, MySQL, Mongo)
    │   ├── models/                    # Base SQLAlchemy and Pydantic models
    │   ├── repositories/              # Generic base repositories (`BasePostgresRepository`, etc.)
    │   └── utilities/                 # String, time, and console printing utilities
    └── scripts/                       # Executable ETL entry points and automation scripts
        └── update_stock_instrument_data.py  # Download and sync master instruments
```

---

## Service Catalog & Lifecycle Management

All domain services are managed and instantiated via [`StockDataManagementContainer`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/container.py). The container acts as the single composition root, wiring shared clients (AWS S3, Upstox API, MongoDB) and injecting [`PostgresUnitOfWork`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/infrastructure/db/postgres_unit_of_work.py) into each service.

### 1. `UpstoxAccessTokenManager`
* **Module**: [`upstox_access_token_manager.py`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/services/upstox_access_token_manager.py)
* **Purpose**: Coordinates Upstox OAuth 2.0 access token retrieval, validity checking, and concurrency protection.
* **Key Mechanisms**:
  - **Double-Checked Locking**: Thread-safe mutex lock (`threading.Lock`) prevents multiple concurrent workers from triggering redundant OAuth refresh flows.
  - **Grace Margin**: Validates that cached tokens in Redis have $> 60$ seconds remaining before considering them valid.
  - **Auto-Expiration Calculation**: Computes TTL based on Upstox's daily token reset schedule (03:30 AM IST).

### 2. `StockInstrumentsService`
* **Module**: [`stock_instruments_service.py`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/services/stock_instruments_service.py)
* **Purpose**: Ingests, normalizes, validates, and syncs complete NSE/BSE instrument lists into PostgreSQL.
* **Key Mechanisms**:
  - **Streaming Mode (`sync_instruments`)**: Memory-efficient JSON parsing via `ijson`, filtering columns against target table schema, and bulk upserting in 1,000-row batches.
  - **Staged Polars Engine Mode (`sync_instruments_new`)**: Reads raw JSON with `PolarsReader`, applies type coercion via `PolarsSchemaValidator`, writes to a staging CSV, loads into a PostgreSQL temporary table (`tmp_stock_instruments_data`), generates an interactive diff report (inserts vs updates), and executes the sync.
  - **Cursor Streaming Generators**: `get_company_instruments_stream` and `get_missing_companies_stream` yield model instances inside active UoW context blocks.

### 3. `CompanyProfileService`
* **Module**: [`company_profile_services.py`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/services/company_profile_services.py)
* **Purpose**: Fetches company overview, fundamental profile, industry sector, and market capitalization.
* **Key Mechanisms**:
  - **Dual Persistence**: Upserts complete nested document payloads into MongoDB (`stock_instruments_profile`), while extracting structured fields (`isin`, `sector`, `company_profile`) for relational storage in PostgreSQL (`company_profile`).
  - **Rate Limiting & Gap Ingestion**: Iterates through instruments lacking profiles with configurable throttle delays (`sleep_time`).

### 4. `StockHistoricalDataService`
* **Module**: [`stock_historical_data_service.py`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/services/stock_historical_data_service.py)
* **Purpose**: Downloads multi-resolution historical candlesticks (minute, hour, day, week, month) from Upstox, archives raw responses in AWS S3, and loads parsed candles into PostgreSQL.
* **Key Mechanisms**:
  - **Interval Retention Limits**: Automatically bounds minute/hourly queries to 2022-01-01 and daily/weekly/monthly queries to 2000-01-01.
  - **Calendar Partitioning**: Splits large date spans into monthly or yearly contiguous chunks (`(first_day, last_day)`).
  - **Incremental Continuation**: Checks `raw_historical_data_info` for the latest imported `to_date` to avoid duplicate downloads.
  - **S3 to DB ETL**: Streams raw JSON from S3, parses OHLCV tuples `[timestamp, open, high, low, close, volume, open_interest]`, executes batch upserts of 5,000 rows into `stock_candle_data`, and updates `processed_timestamp`.

### 5. `CompanyFinanceServices`
* **Module**: [`company_finance_services.py`](file:///home/nikhilnarayanbehera/MyProjects/DataEngineeringPractice/Stock_News_Data_Project/Stock_Data_Service/src/apps/stock_data_management/services/company_finance_services.py)
* **Purpose**: Ingests Balance Sheets, Cash Flow Statements, and Income Statements (P&L) for consolidated and standalone filings.
* **Key Mechanisms**:
  - **Normalized Entity Mapping**: Maps source line items to standardized `FinancialMetric` enums via `FINANCIAL_METRIC_ALIASES`.
  - **Price Unit Normalization**: Standardizes denomination units (Crores, Lakhs) via `FINANCIAL_PRICE_UNITS_ALIASES`.
  - **Relational Header/Record Normalization**: Creates or references statement headers in `financial_statements` and records individual historical data points in `financial_statement_records`.

---

## Models & Repositories: Linkages & Usage

The table below details how models, repositories, and services interconnect through the `PostgresUnitOfWork`:

| Database | Model Class | Repository Class | UoW Attribute | Consuming Service(s) | Role & Operational Logic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | `StockInstrumentsData` | `StockInstrumentsRepository` | `uow.stock_instruments_repository` | `StockInstrumentsService` | Master list of all trading instruments; supports temp-table staging diffs and bulk upserts. |
| **PostgreSQL** | `CompanyProfile` | `CompanyProfileRepository` | `uow.company_profiles_repository` | `CompanyProfileService` | Relational corporate business description and sector classification. |
| **PostgreSQL** | `RawHistoricalDataInfo` | `StockRawHistoricalDataInfoRepository` | `uow.raw_historical_data_info_repository` | `StockHistoricalDataService` | Metadata tracking S3 storage keys, date boundaries, interval resolutions, and ingestion status. |
| **PostgreSQL** | `StockCandleData` | `StockCandleDataRepository` | `uow.stock_candle_data_repository` | `StockHistoricalDataService` | High-volume candlestick time-series table; upserted on `(raw_historical_data_info_id, candle_timestamp)`. |
| **PostgreSQL** | `FinanceDataSource` | `FinanceDataSourceRepository` | `uow.finace_data_source_repository` | `CompanyFinanceServices` | Master table tracking data source providers (e.g. `FinancialDataSourceEnum.UPSTOX`). |
| **PostgreSQL** | `FinancialReportPriceUnits` | `FinancialReportPriceUnitsRepository` | `uow.financial_report_price_units_repository` | `CompanyFinanceServices` | Master table of financial statement currency units (e.g. `PriceUnitEnum.CRORES`). |
| **PostgreSQL** | `FinanceMetrics` | `FinanceMetricsRepository` | `uow.finance_metrics_repository` | `CompanyFinanceServices` | Normalized metric definitions and line items (e.g. `FinancialMetric.TOTAL_REVENUE`). |
| **PostgreSQL** | `FinancialPeriodTypes` | `FinancialPeriodTypesRepository` | `uow.financial_period_types_repository` | `CompanyFinanceServices` | Reporting period definitions with exact ending date and fiscal quarter enum. |
| **PostgreSQL** | `FinancialStatement` | `FinancialStatementRepository` | `uow.financial_statements_repository` | `CompanyFinanceServices` | Statement header records linking ISIN, filing type, period type, and price unit. |
| **PostgreSQL** | `FinancialStatementRecords`| `FinancialStatementRecordsRepository`| `uow.financial_statement_records_repository`| `CompanyFinanceServices` | Numeric values of financial metrics for each period; upserted on conflict. |
| **MongoDB** | `StockInstrumentsProfile` | `StockInstrumentsProfileRepository` | *Direct Service Injection* | `CompanyProfileService` | MongoDB collection storing complete fundamental JSON profiles and market cap data. |
| **PostgreSQL** | *(Cross-table Query)* | `CompanyProfieQueries` | `uow.company_profile_queries_repository` | `StockInstrumentsService`, `CompanyProfileService` | Performs outer-join queries to stream instruments lacking company profiles. |

---

## Data Pipelines & Workflows

### 1. Historical Candlestick Ingestion Pipeline

```
[Trigger Fetch] ──> [StockHistoricalDataService]
                          │
                          ├─ 1. Determine Date Boundaries (2000/2022 -> Today)
                          ├─ 2. Query Postgres for Last Imported Date (Incremental)
                          ├─ 3. Split into Monthly/Yearly Chunks
                          │
                          ▼
            [Upstox API: /v3/historical-candle/...]
                          │
                          ▼
          [Upload Raw JSON to AWS S3 Bucket]
                          │
                          ▼
   [Upsert Batch Metadata in raw_historical_data_info]
                          │
                          ▼
             [Stream JSON from AWS S3]
                          │
                          ├─ Parse OHLCV Candles
                          └─ Batch Upsert into stock_candle_data (5,000 / batch)
                          │
                          ▼
  [Update raw_historical_data_info.processed_timestamp]
```

### 2. Corporate Financial Statements Ingestion Pipeline

```
[Trigger Financial Sync (ISIN)] ──> [CompanyFinanceServices]
                                             │
                                             ▼
                      [Upstox Fundamental Client: Balance/CashFlow/Income]
                                             │
                                             ▼
                               [Validate Price Unit & Metric Aliases]
                                             │
                                             ▼
                                  [PostgresUnitOfWork (UoW)]
                                             │
                        ┌────────────────────┴────────────────────┐
                        ▼                                         ▼
            [Upsert Statement Header]                 [Upsert Financial Period]
            (financial_statements)                   (financial_period_types)
                        │                                         │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
                            [Upsert Line-Item Record Values]
                             (financial_statement_records)
```

---

## Polyglot Storage Design

1. **PostgreSQL 15+**:
   - Primary operational datastore for relational metadata, financial metrics, and high-volume time-series candlestick data.
   - Leverages `ON CONFLICT DO UPDATE` for idempotent upsert operations.
2. **MongoDB**:
   - Houses semi-structured and rapidly changing corporate fundamental profile documents (`stock_instruments_profile`).
   - Managed via `BaseMongoRepository` and validated through Pydantic model definitions.
3. **AWS S3**:
   - Serves as the raw, immutable data lake for historical candle JSON responses, partitioned by `historical-data/{instrument_key}/{interval}/{from_date} - {to_date}`.
4. **Redis**:
   - Caches short-lived OAuth 2.0 access tokens and expiration timestamps to minimize external authorization requests.

---

## Getting Started & Operations

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- MongoDB 6.0+
- Redis 7.0+
- AWS Account with S3 Bucket Access

### Environment Configuration
Create a `.env` file in the project root with the following variables:

```ini
# PostgreSQL
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=stock_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=stock_data_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
AWS_HISTORICAL_DATA_S3_BUCKET=your-historical-data-bucket

# Upstox API
UPSTOX_API_KEY=your_upstox_api_key
UPSTOX_API_SECRET=your_upstox_api_secret
UPSTOX_REDIRECT_URI=https://127.0.0.1:5000/
```

### Installation
```bash
# Install package and dependencies in editable mode
pip install -e ".[dev]"
```

### Running Database Migrations
```bash
# Apply migrations to latest revision
alembic upgrade head
```

### Running the Instrument Sync Script
```bash
# Downloads, unpacks, and synchronizes master stock instruments from Upstox
python src/scripts/update_stock_instrument_data.py
```
