
from core.infrastructure.aws.Storage.s3_storage import S3Storage
from core.infrastructure.aws.aws_client_container import AWSClientContainer
from core.infrastructure.aws.aws_session import create_aws_session


class AwsClient:
    def __init__(self, region: str | None = None):
        aws_session = create_aws_session(region)
        self._aws_client_container = AWSClientContainer(aws_session=aws_session)
        self._s3_storage = S3Storage(self._aws_client_container)
        
        
    def get_s3_storage(self):
        return self._s3_storage