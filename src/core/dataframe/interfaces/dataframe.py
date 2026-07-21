from abc import ABC, abstractmethod


class IDataFrame(ABC):
    @property
    @abstractmethod
    def native(self):
        pass
    
    @property
    @abstractmethod
    def columns(self):
        pass

    @property
    @abstractmethod
    def shape(self):
        pass
    
    @abstractmethod
    def to_dict(self):
        pass