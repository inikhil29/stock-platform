import boto3

from core.config.aws_settings import aws_settings

def create_aws_session(region=aws_settings.AWS_REGION):
    return boto3.Session(
        aws_access_key_id=aws_settings.AWS_ACCESS_KEY,
        aws_secret_access_key=aws_settings.AWS_SECRET_KEY,
        region_name=region
    )