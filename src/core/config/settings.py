from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):

    REDIS_HOST: str
    REDIS_PROTOCOL: str
    REDIS_PORT: int
    REDIS_NAMESPACE: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def REDIS_URL(self):
        return f"{self.REDIS_PROTOCOL}://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def BASE_DIR(self):
        return (
            Path(__file__).resolve().parent.parent.parent
        )


settings = Settings()
BASE_DIR = settings.BASE_DIR