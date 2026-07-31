from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class AwsSettings(BaseSettings):

    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    AWS_HISTORICAL_DATA_S3_BUCKET:str = 'stock-data-app'

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


aws_settings = AwsSettings()