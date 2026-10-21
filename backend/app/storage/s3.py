"""Document file storage manager (AWS S3 with local disk fallback).

Stores raw uploaded enterprise knowledge files (PDF, Word, Excel, PPT)
prior to text extraction and chunking.
"""

import os
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DocumentStorageManager:
    """Manages raw document persistence in AWS S3 or local development fallback."""

    def __init__(self) -> None:
        self.s3_client = None
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                import boto3

                self.s3_client = boto3.client(
                    "s3",
                    region_name=settings.aws_region,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    endpoint_url=settings.s3_endpoint_url,
                )
            except Exception as exc:
                logger.warning("Failed to initialize AWS S3 client; falling back to local storage", error=str(exc))

        # Local storage fallback
        self.local_dir = Path(settings.local_storage_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_obj: BinaryIO, filename: str, content_type: str | None = None) -> str:
        """Upload an uploaded enterprise file to S3 or local storage and return its URI."""
        if self.s3_client and settings.s3_bucket_name:
            s3_key = f"raw_documents/{filename}"
            extra_args = {"ContentType": content_type} if content_type else {}
            self.s3_client.upload_fileobj(file_obj, settings.s3_bucket_name, s3_key, ExtraArgs=extra_args)
            return f"s3://{settings.s3_bucket_name}/{s3_key}"

        # Local filesystem fallback
        destination = self.local_dir / filename
        file_obj.seek(0)
        with open(destination, "wb") as f:
            f.write(file_obj.read())
        return str(destination.resolve())
