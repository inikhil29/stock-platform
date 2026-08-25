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
        df = dataframe.native if isinstance(dataframe, PolarsDataFrame) else dataframe
        if isinstance(df, pl.LazyFrame):
            df.collect().write_csv(path, **kwargs)
        else:
            dataframe.write_csv(path, **kwargs)
            df.write_csv(path, **kwargs)

    def write_parquet(
        self,
        dataframe: PolarsDataFrame,
        path: str,
        **kwargs,
    ):
        df = dataframe.native if isinstance(dataframe, PolarsDataFrame) else dataframe
        if isinstance(df, pl.LazyFrame):
            df.collect().write_parquet(path, **kwargs)
        else:
            dataframe.write_parquet(path, **kwargs)
            df.write_parquet(path, **kwargs)

    def write_json(
        self,
        dataframe: PolarsDataFrame,
        path: str,
        **kwargs,
    ):
        df = dataframe.native if isinstance(dataframe, PolarsDataFrame) else dataframe
        if isinstance(df, pl.LazyFrame):
            df.collect().write_json(path, **kwargs)
        else:
            dataframe.write_json(path, **kwargs)
            df.write_json(path, **kwargs)

    def write_database(
        self,
        dataframe: PolarsDataFrame,
        table: str,
        connection,
        **kwargs,
    ):
        df = dataframe.native if isinstance(dataframe, PolarsDataFrame) else dataframe
        if isinstance(df, pl.LazyFrame):
            df.collect().write_database(table_name=table, connection=connection, **kwargs)
        else:
            df.write_database(table_name=table, connection=connection, **kwargs)
