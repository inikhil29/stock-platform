from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class DatabasSettings(BaseSettings):
    
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    
    POSTGRES_HOST:str
    POSTGRES_USER:str
    POSTGRES_PASSWORD:str
    POSTGRES_PORT:str
        
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def MYSQL_DATABASE_URI(self):
        password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}"
    
    @property
    def POSTGRES_DATABASE_URI(self):
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"