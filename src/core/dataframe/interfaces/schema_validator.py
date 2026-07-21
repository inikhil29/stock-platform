from abc import ABC, abstractmethod

from core.dataframe.interfaces.dataframe import IDataFrame


class ISchemaValidator(ABC):

    @abstractmethod
    def apply(
        self,
        dataframe: IDataFrame,
        schema: dict,
    ) -> IDataFrame:
        """
        Validate and apply schema to dataframe.
        """
        pass
