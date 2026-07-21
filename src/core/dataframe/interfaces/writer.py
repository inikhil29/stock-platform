from abc import ABC, abstractmethod
from core.dataframe.interfaces.dataframe import IDataFrame


class IDataWriter(ABC):

    @abstractmethod
    def write_csv(
        self,
        dataframe: IDataFrame,
        path: str,
        **kwargs,
    ):
        pass

    @abstractmethod
    def write_parquet(
        self,
        dataframe: IDataFrame,
        path: str,
        **kwargs,
    ):
        pass

    @abstractmethod
    def write_json(
        self,
        dataframe: IDataFrame,
        path: str,
        **kwargs,
    ):
        pass

    @abstractmethod
    def write_database(
        self,
        dataframe: IDataFrame,
        table: str,
        connection,
        **kwargs,
    ):
        pass