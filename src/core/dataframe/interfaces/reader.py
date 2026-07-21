from abc import ABC, abstractmethod
from core.dataframe.interfaces.dataframe import IDataFrame


class IDataReader(ABC):

    @abstractmethod
    def read_csv(self, path: str, **kwargs) -> IDataFrame:
        pass

    @abstractmethod
    def read_parquet(self, path: str, **kwargs) -> IDataFrame:
        pass

    @abstractmethod
    def read_excel(self, path: str, **kwargs) -> IDataFrame:
        pass

    @abstractmethod
    def read_json(self, path: str, **kwargs) -> IDataFrame:
        pass

    @abstractmethod
    def read_database(self, query: str, connection) -> IDataFrame:
        pass