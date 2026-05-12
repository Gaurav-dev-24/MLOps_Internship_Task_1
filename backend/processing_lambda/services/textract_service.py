"""
services/textract_service.py (processing_lambda)

AWS Textract integration service.

Responsibilities:
  - Call analyze_document() with TABLES and FORMS feature types.
  - Return the raw Textract response blocks for the parser.
  - Wrap all ClientError exceptions as TextractProcessingException.
"""

import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from processing_lambda.exceptions.custom_exceptions import TextractProcessingException
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

# Feature types to enable — TABLES extracts tabular line items,
# FORMS extracts key-value pairs (vendor name, dates, totals, etc.)
_FEATURE_TYPES: list[str] = ["TABLES", "FORMS"]

_AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")


class TextractService:
    """Handles all AWS Textract document analysis calls."""

    def __init__(self) -> None:
        self._client = boto3.client("textract", region_name=_AWS_REGION)

    def analyze_document(
        self, bucket_name: str, file_key: str
    ) -> list[dict[str, Any]]:
        """
        Submit a document stored in S3 to Textract for synchronous analysis.

        Uses analyze_document (synchronous) which supports both FORMS and TABLES.
        For PDFs > 1 page at scale, this should be migrated to the async
        start_document_analysis / get_document_analysis pattern.

        Args:
            bucket_name: S3 bucket containing the uploaded invoice.
            file_key:    S3 object key of the invoice file.

        Returns:
            List of raw Textract Block objects from the response.

        Raises:
            TextractProcessingException: If Textract returns a ClientError.
        """
        logger.info(
            "Submitting document to Textract. bucket=%s key=%s features=%s",
            bucket_name,
            file_key,
            _FEATURE_TYPES,
        )
        try:
            response: dict[str, Any] = self._client.analyze_document(
                Document={
                    "S3Object": {
                        "Bucket": bucket_name,
                        "Name": file_key,
                    }
                },
                FeatureTypes=_FEATURE_TYPES,
            )
        except ClientError as exc:
            logger.error(
                "Textract analyze_document failed. bucket=%s key=%s error=%s",
                bucket_name,
                file_key,
                str(exc),
            )
            raise TextractProcessingException(
                f"Textract analysis failed for s3://{bucket_name}/{file_key}."
            ) from exc

        blocks: list[dict[str, Any]] = response.get("Blocks", [])
        logger.info(
            "Textract analysis complete. bucket=%s key=%s block_count=%d",
            bucket_name,
            file_key,
            len(blocks),
        )
        return blocks
