"""Storage package: AWS S3 and document blob persistence."""

from app.storage.s3 import DocumentStorageManager

__all__ = ["DocumentStorageManager"]
