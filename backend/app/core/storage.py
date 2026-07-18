"""S3-compatible object storage for uploaded images.

Talks to MinIO today via boto3's S3 client with S3_ENDPOINT_URL pointed at the
MinIO container. Moving to real AWS S3 later is just an env var change: unset
S3_ENDPOINT_URL (boto3 then defaults to AWS) and point S3_PUBLIC_URL_BASE at
the bucket's/CloudFront's public URL — no code change needed.
"""

import os
import uuid
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.exceptions import ValidationError

BUCKET = os.environ.get("S3_BUCKET", "contoso-images")
PUBLIC_URL_BASE = os.environ.get("S3_PUBLIC_URL_BASE", "").rstrip("/")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

_PUBLIC_READ_POLICY = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::%s/*"
        }
    ]
}"""


@lru_cache
def get_s3_client():
    kwargs = {
        "region_name": os.environ.get("S3_REGION", "us-east-1"),
        "aws_access_key_id": os.environ.get("S3_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.environ.get("S3_SECRET_ACCESS_KEY"),
    }
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("s3", **kwargs)


def ensure_bucket() -> None:
    """Idempotent: creates the bucket with a public-read policy if it doesn't exist yet."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=BUCKET)
        return
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") not in ("404", "NoSuchBucket"):
            raise

    client.create_bucket(Bucket=BUCKET)
    client.put_bucket_policy(Bucket=BUCKET, Policy=_PUBLIC_READ_POLICY % BUCKET)


def upload_image(file: UploadFile) -> str:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValidationError("File must be an image")

    contents = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise ValidationError("Image exceeds the 5MB upload limit")

    ext = os.path.splitext(file.filename or "")[1] or ""
    key = f"products/{uuid.uuid4().hex}{ext}"

    get_s3_client().put_object(Bucket=BUCKET, Key=key, Body=contents, ContentType=file.content_type)
    return f"{PUBLIC_URL_BASE}/{key}"
