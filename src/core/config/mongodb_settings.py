from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class MongoDBSettings(BaseSettings):
    
    MONGODB_USER:str
    MONGODB_PASSWORD:str
    MONGODB_PORT:int
    MONGODB_HOST:str
        
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def MONGO_URI(self):
        password = quote_plus(self.MONGODB_PASSWORD)
        return f"mongodb://{self.MONGODB_USER}:{password}@{self.MONGODB_HOST}:{self.MONGODB_PORT}"