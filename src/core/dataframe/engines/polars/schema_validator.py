import polars as pl

from core.dataframe.engines.polars.dataframe import PolarsDataFrame
from core.dataframe.interfaces.schema_validator import ISchemaValidator


class PolarsSchemaValidator(ISchemaValidator):

    def apply(
        self,
        dataframe: PolarsDataFrame,
        schema: dict,
    ) -> PolarsDataFrame:

        df = dataframe.native

        missing = [
            column
            for column in schema
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        expressions = [
            pl.col(column).cast(dtype)
            for column, dtype in schema.items()
        ]

        df = df.with_columns(expressions)

        return PolarsDataFrame(df)