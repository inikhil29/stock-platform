upstox-service/
│
├── .env
├── pyproject.toml
├── README.md
│
├── src/
│   └── upstox/
│
│       ├── main.py                     # Entry point (manual run / CLI)
│
│       ├── config/
│       │   └── settings.py             # Pydantic settings (loads .env)
│
│       ├── infrastructure/
│       │   ├── db/
│       │   │   ├── engine.py           # create_engine(settings.DB_URL)
│       │   │   ├── session.py          # SessionLocal
│       │   │   └── db_context.py       # ✅ YOUR contextmanager lives HERE
│       │   │
│       │   └── clients/
│       │       ├── upstox_client.py    # HTTP client
│       │       ├── auth_client.py
|               └── http_client.py
│
│       ├── services/                  # API-specific logic
│       │   ├── base_service.py
│       │   ├── historical_data_service.py
│       │   ├── market_quote_service.py
│       │   ├── instrument_service.py
│       │   └── order_service.py
│
│       ├── pipelines/                 # ETL orchestration (IMPORTANT)
│       │   ├── stock_pipeline.py
│       │   ├── instrument_pipeline.py
│       │   └── order_pipeline.py
│
│       ├── transformers/              # Pure data transformation
│       │   ├── stock_transformer.py
│       │   └── instrument_transformer.py
│
│       ├── loaders/                   # ✅ Uses DB session (ETL writes)
│       │   ├── stock_loader.py
│       │   └── instrument_loader.py
│
│       ├── repositories/              # Optional (non-ETL DB access)
│       │   └── stock_repository.py
│
│       ├── models/                    # SQLAlchemy models
│       │   ├── stock_model.py
│       │   └── instrument_model.py
│
│       ├── schemas/                   # Pydantic validation
│       │   ├── stock_schema.py
│       │   └── instrument_schema.py
│
│       ├── jobs/                      # Airflow / cron entry points
│       │   ├── run_stock_etl.py
│       │   └── run_instrument_etl.py
│
│       ├── exceptions/
│       │   └── custom_exceptions.py
│
│       └── utils/
│           └── helpers.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── scripts/