from pydantic import ConfigDict
from core.config.mongodb_settings import MongoDBSettings
from core.config.mysql_settings import MySQLDatabasSettings

class UpstoxSettings(MySQLDatabasSettings, MongoDBSettings):

    UPSTOX_API_KEY:str
    UPSTOX_LIVE_URL:str
    UPSTOX_REDIRECT_URI:str
    UPSTOX_API_SECRET:str
    
    UPSTOX_MYSQL_DATABASE: str
    
    UPSTOX_MONGODB_DATABASE:str
        
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def UPSTOX_DATABASE_URL(self):
        return f"{self.DATABASE_URL}/{self.UPSTOX_MYSQL_DATABASE}"
    
    @property
    def UPSTOX_MONGO_URI(self):
        return f"{self.MONGO_URI}/{self.UPSTOX_MONGODB_DATABASE}?authSource={self.UPSTOX_MONGODB_DATABASE}"
        


settings = UpstoxSettings()