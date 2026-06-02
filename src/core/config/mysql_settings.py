from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class MySQLDatabasSettings(BaseSettings):
    
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
        
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def DATABASE_URL(self):
        password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}"