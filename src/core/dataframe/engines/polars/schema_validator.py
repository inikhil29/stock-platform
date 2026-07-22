import polars as pl
from core.dataframe.engines.polars.dataframe import PolarsDataFrame
from core.dataframe.interfaces.schema_validator import ISchemaValidator
from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, Date

class PolarsSchemaValidator(ISchemaValidator):
    def __init__(self):
        self.TYPE_MAPPING = {
            Integer: pl.Int64,
            String: pl.String,
            Text: pl.String,
            Float: pl.Float64,
            Boolean: pl.Boolean,
            Date: pl.Date,
            DateTime: pl.Datetime,
        }

    def apply(
        self,
        dataframe: PolarsDataFrame,
        schema: dict,
        ignore_columns: list[str]| None = None
    ) -> PolarsDataFrame:

        df = dataframe.native
        ignore_columns = set(ignore_columns or [])

        missing = []
        expressions = []
        if ignore_columns:
            schema = {k:v for k,v in schema.items() if k not in ignore_columns}
        for column in schema:
            if column not in df.columns:
                missing.append(column)
                continue

        expressions = [
            pl.col(column).cast(self.TYPE_MAPPING.get(type(dtype)))
            for column, dtype in schema.items()
        ]
        if missing:
            print(f"Missing columns: {missing}")
        df = df.with_columns(expressions)
        return PolarsDataFrame(df).select(list(schema.keys()))