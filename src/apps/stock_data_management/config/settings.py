from pydantic import ConfigDict
from core.config.mongodb_settings import MongoDBSettings
from core.config.sql_database_settings import DatabasSettings


class StockDataManagementSettings(DatabasSettings, MongoDBSettings):

    UPSTOX_API_KEY: str
    UPSTOX_LIVE_URL: str
    UPSTOX_REDIRECT_URI: str
    UPSTOX_API_SECRET: str

    STOCK_INFO_MYSQL_DATABASE: str

    UPSTOX_MONGODB_DATABASE: str

    STOCK_INFO_POSTGRES_DATABASE: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def STOCK_INFO_MYSQL_DATABASE_URI(self):
        return f"{self.MYSQL_DATABASE_URI}/{self.STOCK_INFO_MYSQL_DATABASE}"

    @property
    def STOCK_INFO_POSTGRES_DATABASE_URI(self):
        return f"{self.POSTGRES_DATABASE_URI}/{self.STOCK_INFO_POSTGRES_DATABASE}"

    @property
    def UPSTOX_MONGO_URI(self):
        return f"{self.MONGO_URI}/{self.UPSTOX_MONGODB_DATABASE}?authSource={self.UPSTOX_MONGODB_DATABASE}"


settings = StockDataManagementSettings()
