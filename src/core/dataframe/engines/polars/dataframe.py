

from core.dataframe.interfaces.dataframe import IDataFrame
import polars as pl


class PolarsDataFrame(IDataFrame):

    def __init__(self, dataframe: pl.DataFrame | pl.LazyFrame):

        self._df = dataframe

    @property
    def native(self) -> pl.DataFrame | pl.LazyFrame:
        return self._df

    @property
    def columns(self) -> list[str]:
        return self._df.columns

    @property
    def shape(self) -> tuple[int, int]:
        if isinstance(self._df, pl.LazyFrame):
            return self._df.collect().shape

        return self._df.shape

    def to_dict(self):

        if isinstance(self._df, pl.LazyFrame):
            return self._df.collect().to_dict(as_series=False)

        return self._df.to_dict(as_series=False)


    def collect(self):
    
        if isinstance(self._df, pl.LazyFrame):
            return PolarsDataFrame(self._df.collect())
        
        return self    
    
    
    def write_csv(self, path: str, **kwargs):
        self._df.write_csv(path, **kwargs)
        
    def write_parquet(self, path: str, **kwargs):
            self._df.write_parquet(path, **kwargs)
            
            
    def write_json(self, path:str, **kwargs,):
        self._df.write_json(path, **kwargs)
        
    def write_database(
        self,
        table: str,
        connection,
        **kwargs,
    ):
        self._df.write_database(table_name=table, connection=connection, **kwargs)
        