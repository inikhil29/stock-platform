from pydantic import ConfigDict
from core.config.mongodb_settings import MongoDBSettings
from core.config.sql_database_settings import DatabasSettings


class NewsDataIOApiSettings(DatabasSettings, MongoDBSettings):

    NEWS_DATA_IO_MYSQL_DATABASE: str
    NEWS_DATA_IO_LIVE_URL: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def NEWS_DATA_IO_DATABASE_URL(self):
        return f"{self.MYSQL_DATABASE_URI}/{self.NEWS_DATA_IO_MYSQL_DATABASE}"


settings = NewsDataIOApiSettings()