from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class Settings(BaseSettings):

    UPSTOX_API_KEY:str
    UPSTOX_LIVE_URL:str
    UPSTOX_REDIRECT_URI:str
    UPSTOX_API_SECRET:str
    
    REDIS_HOST:str
    REDIS_PROTOCOL:str
    REDIS_PORT:int
    REDIS_UPSTOX_DB:int
    REDIS_NAMESPACE:str
    
    UPSTOX_MYSQL_HOST: str
    UPSTOX_MYSQL_USER: str
    UPSTOX_MYSQL_PASSWORD: str
    UPSTOX_MYSQL_DATABASE: str
    
    UPSTOX_MONGODB_DATABASE:str
    UPSTOX_MONGODB_USER:str
    UPSTOX_MONGODB_PASSWORD:str
    UPSTOX_MONGODB_PORT:int
    UPSTOX_MONGODB_HOST:str
        
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def UPSTOX_REDIS_URL(self):
        return f"{self.REDIS_PROTOCOL}://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_UPSTOX_DB}"
    
    @property
    def UPSTOX_DATABASE_URL(self):
        password = quote_plus(self.UPSTOX_MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.UPSTOX_MYSQL_USER}:{password}@{self.UPSTOX_MYSQL_HOST}/{self.UPSTOX_MYSQL_DATABASE}"
    
    @property
    def UPSTOX_MONGO_URI(self):
        password = quote_plus(self.UPSTOX_MONGODB_PASSWORD)
        return f"mongodb://{self.UPSTOX_MONGODB_USER}:{password}@{self.UPSTOX_MONGODB_HOST}:{self.UPSTOX_MONGODB_PORT}/{self.UPSTOX_MONGODB_DATABASE}?authSource={self.UPSTOX_MONGODB_DATABASE}"
        


settings = Settings()