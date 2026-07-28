

from pathlib import Path

from sqlalchemy.engine import Engine

from core.dataframe.engines.polars.dataframe import PolarsDataFrame
from core.dataframe.interfaces.reader import IDataReader
import polars as pl


class PolarsReader(IDataReader):
    def read_csv(self, path: str, **kwargs):
        source = Path(path)
        dataframe = pl.read_csv(
            source,
            **kwargs,
        )

        return PolarsDataFrame(dataframe)

    def read_parquet(self, path: str, **kwargs):
        source = Path(path)
        dataframe = pl.read_parquet(
            source,
            **kwargs,
        )

        return PolarsDataFrame(dataframe)

    def read_excel(self, path: str, **kwargs):
        source = Path(path)
        dataframe = pl.read_parquet(
            source,
            **kwargs,
        )

        return PolarsDataFrame(dataframe)

    def read_json(self, path: str, **kwargs):
        source = Path(path)
        dataframe = pl.read_json(
            source,
            **kwargs,
        )

        return PolarsDataFrame(dataframe)

    def read_ndjson(self, path: str, **kwargs):
        source = Path(path)
        dataframe = pl.read_ndjson(
            source,
            **kwargs,
        )

        return PolarsDataFrame(dataframe)

    def read_database(self, query: str, connection: Engine, **kwargs):
        dataframe = pl.read_database(
            query=query,
            connection=connection
            ** kwargs,
        )

        return PolarsDataFrame(dataframe)
    
    def read_dicts(self, data: list[dict] , **kwargs) -> PolarsDataFrame:
            dataframe = pl.from_dicts(
                data,
                **kwargs,
            )
    
            return PolarsDataFrame(dataframe)
