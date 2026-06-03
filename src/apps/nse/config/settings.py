from pydantic import ConfigDict
from core.config.mongodb_settings import MongoDBSettings
from core.config.mysql_settings import MySQLDatabasSettings

class NSEApiSettings(MySQLDatabasSettings, MongoDBSettings):
    
    NSE_MYSQL_DATABASE: str
    NSE_LIVE_URL:str
            
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def NSE_DATABASE_URL(self):
        return f"{self.DATABASE_URL}/{self.NSE_MYSQL_DATABASE}"
        


settings = NSEApiSettings()