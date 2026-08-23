
from contextlib import contextmanager
from io import BytesIO
from typing import BinaryIO, Generator, Iterator

from botocore.exceptions import ClientError

from core.infrastructure.aws.aws_client_container import AWSClientContainer


class S3Storage:

    def __init__(self, aws_client: AWSClientContainer):
        self._client = aws_client.get_s3_client()

    def upload_file(
        self,
        bucket: str,
        key: str,
        file_path: str
    ) -> None:

        self._client.upload_file(
            Filename=file_path,
            Bucket=bucket,
            Key=key
        )

    def upload_bytes(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str | None = None
    ) -> None:

        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            **extra_args
        )

    def upload_fileobj(
        self,
        bucket: str,
        key: str,
        fileobj: BinaryIO
    ) -> None:

        self._client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=bucket,
            Key=key
        )

    def download_file(
        self,
        bucket: str,
        key: str,
        destination: str
    ) -> None:

        self._client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=destination
        )

    def download_bytes(
        self,
        bucket: str,
        key: str
    ) -> bytes:

        response = self._client.get_object(
            Bucket=bucket,
            Key=key
        )

        return response["Body"].read()

    @contextmanager
    def download_stream(
        self,
        bucket: str,
        key: str
    ) -> Generator[BinaryIO, None, None]:

        response = self._client.get_object(
            Bucket=bucket,
            Key=key
        )
        body = response["Body"]
        try:

            yield body
        finally:
            body.close()

    def exists(
        self,
        bucket: str,
        key: str
    ) -> bool:

        try:

            self._client.head_object(
                Bucket=bucket,
                Key=key
            )

            return True

        except ClientError as ex:

            if ex.response["Error"]["Code"] == "404":
                return False

            raise

    def delete(
        self,
        bucket: str,
        key: str
    ) -> None:

        self._client.delete_object(
            Bucket=bucket,
            Key=key
        )

    def copy(
        self,
        source_bucket: str,
        source_key: str,
        destination_bucket: str,
        destination_key: str
    ) -> None:

        self._client.copy_object(
            Bucket=destination_bucket,
            Key=destination_key,
            CopySource={
                "Bucket": source_bucket,
                "Key": source_key
            }
        )

    def list_objects(
        self,
        bucket: str,
        prefix: str = ""
    ) -> list[dict]:

        paginator = self._client.get_paginator(
            "list_objects_v2"
        )

        objects = []

        for page in paginator.paginate(
            Bucket=bucket,
            Prefix=prefix
        ):

            objects.extend(
                page.get("Contents", [])
            )

        return objects

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600
    ) -> str:

        return self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": key
            },
            ExpiresIn=expires_in
        )
