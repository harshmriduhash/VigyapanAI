import boto3
from botocore.client import Config
from typing import Optional
from config import get_settings


def _client():
    settings = get_settings()
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def upload_file(file_path: str, key: str) -> str:
    s3 = _client()
    bucket = get_settings().s3_bucket
    s3.upload_file(file_path, bucket, key)
    return f"s3://{bucket}/{key}"


def presign_url(key: str, expires: int = 3600) -> str:
    s3 = _client()
    settings = get_settings()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires,
    )


def presign_upload(key: str, expires: int = 3600) -> dict:
    s3 = _client()
    settings = get_settings()
    return s3.generate_presigned_post(
        Bucket=settings.s3_bucket,
        Key=key,
        ExpiresIn=expires,
    )

