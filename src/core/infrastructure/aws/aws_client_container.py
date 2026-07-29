from botocore.config import Config
from mypy_boto3_s3 import S3Client

class AWSClientContainer:
    def __init__(self, aws_session):


        config = Config(

            retries={
                "max_attempts": 5,
                "mode": "standard"
            }
        )
        self._session = aws_session
        self._s3 = self._session.client('s3', config=config)

    def get_s3_client(self) -> S3Client:
        return self._s3
