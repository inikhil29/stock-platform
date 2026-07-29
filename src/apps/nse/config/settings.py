from pydantic import ConfigDict
from core.config.mongodb_settings import MongoDBSettings
from core.config.sql_database_settings import DatabasSettings


class NSEApiSettings(DatabasSettings, MongoDBSettings):

    NSE_MYSQL_DATABASE: str
    NSE_LIVE_URL: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def NSE_MYSQL_DATABASE_URI(self):
        return f"{self.MYSQL_DATABASE_URI}/{self.NSE_MYSQL_DATABASE}"

    @property
    def UPSTOX_MONGO_URI(self):
        return f"{self.MONGO_URI}/{self.UPSTOX_MONGODB_DATABASE}?authSource={self.UPSTOX_MONGODB_DATABASE}"


settings = NSEApiSettings()
