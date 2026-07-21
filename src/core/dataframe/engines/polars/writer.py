from core.dataframe.engines.polars.dataframe import PolarsDataFrame
import polars as pl

from core.dataframe.interfaces.writer import IDataWriter


class PolarsDataWriter(IDataWriter):

    def write_csv(
        self,
        dataframe: PolarsDataFrame,
        path: str,
        **kwargs,
    ):
        if isinstance(dataframe, pl.LazyFrame):
            dataframe.collect().write_csv(path, **kwargs)
        else:
            dataframe.write_csv(path, **kwargs)

    def write_parquet(
        self,
        dataframe: PolarsDataFrame,
        path: str,
        **kwargs,
    ):
        if isinstance(dataframe, pl.LazyFrame):
            dataframe.collect().write_parquet(path, **kwargs)
        else:
            dataframe.write_parquet(path, **kwargs)

    def write_json(
        self,
        dataframe: PolarsDataFrame,
        path: str,
        **kwargs,
    ):
        if isinstance(dataframe, pl.LazyFrame):
            dataframe.collect().write_json(path, **kwargs)
        else:
            dataframe.write_json(path, **kwargs)

    def write_database(
        self,
        dataframe: PolarsDataFrame,
        table: str,
        connection,
        **kwargs,
    ):
        if isinstance(dataframe, pl.LazyFrame):
            dataframe.collect().write_database(table=table, connection=connection, **kwargs)
        else:
            dataframe.write_parquet(table=table, connection=connection, **kwargs)
