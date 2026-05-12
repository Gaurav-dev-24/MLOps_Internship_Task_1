"""
services/s3_service.py (api_lambda)

S3 presigned-URL generation service.

Responsibilities:
  - Generate a time-limited PUT presigned URL for direct client uploads.
  - Construct the S3 object key (prefix + sanitised filename).

No business logic from other domains lives here.
"""

import logging
import uuid
import os

import boto3
from botocore.exceptions import ClientError

from config.settings import settings
from exceptions.custom_exceptions import S3UploadException
from utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

# S3 key prefix — all uploaded invoices land under this prefix
_KEY_PREFIX: str = "uploads"


class S3Service:
    """Handles S3 presigned URL generation for invoice uploads."""

    def __init__(self) -> None:
        self._client = boto3.client("s3", region_name=settings.AWS_REGION)

    def generate_presigned_url(self, file_name: str) -> tuple[str, str]:
        """
        Generate a presigned PUT URL that allows a client to upload a file
        directly to S3 without routing the binary through the Lambda.

        The S3 key is constructed as:
            uploads/<uuid>_<sanitised_file_name>

        This ensures uniqueness even when the same filename is uploaded
        multiple times.

        Args:
            file_name: Original filename from the client (validated upstream).

        Returns:
            Tuple of (presigned_url, file_key) where:
              - presigned_url is the time-limited PUT URL for the client to use.
              - file_key is the S3 object key (saved to DynamoDB as s3_path).

        Raises:
            S3UploadException: If boto3 fails to generate the presigned URL.
        """
        sanitised: str = os.path.basename(file_name).replace(" ", "_")
        file_key: str = f"{_KEY_PREFIX}/{uuid.uuid4()}_{sanitised}"

        logger.info(
            "Generating S3 presigned PUT URL. bucket=%s key=%s expiry=%ds",
            settings.S3_BUCKET_NAME,
            file_key,
            settings.PRESIGNED_URL_EXPIRY,
        )

        try:
            presigned_url: str = self._client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.S3_BUCKET_NAME,
                    "Key": file_key,
                    "ContentType": self._content_type_for(file_name),
                },
                ExpiresIn=settings.PRESIGNED_URL_EXPIRY,
            )
        except ClientError as exc:
            logger.error(
                "Failed to generate presigned URL. bucket=%s key=%s error=%s",
                settings.S3_BUCKET_NAME,
                file_key,
                str(exc),
            )
            raise S3UploadException(
                "Could not generate S3 upload URL. Please try again."
            ) from exc

        logger.info("Presigned URL generated successfully. key=%s", file_key)
        return presigned_url, file_key

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _content_type_for(file_name: str) -> str:
        """Map a file extension to its MIME content type."""
        ext: str = os.path.splitext(file_name)[-1].lower()
        mapping: dict[str, str] = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }
        return mapping.get(ext, "application/octet-stream")
