"""
services/queue_service.py (processing_lambda)

SQS utility service for the processing pipeline.

Current responsibilities:
  - Delete a successfully processed message from the SQS queue.
  - This prevents re-processing after a successful Lambda invocation
    when the Lambda is not set to auto-delete on success (useful in
    manual error-recovery scenarios).

Note: AWS Lambda automatically deletes SQS messages when the handler
returns successfully. This service is retained for explicit control
and future use (e.g., sending to a DLQ, publishing metrics).
"""

import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from processing_lambda.exceptions.custom_exceptions import QueueServiceException
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

_AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")


class QueueService:
    """Handles SQS operations for the processing pipeline."""

    def __init__(self) -> None:
        self._client = boto3.client("sqs", region_name=_AWS_REGION)

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """
        Delete a processed SQS message to prevent re-delivery.

        Call this only after the full processing pipeline has completed
        successfully (Textract → parser → DynamoDB).

        Args:
            queue_url:      Full URL of the SQS queue.
            receipt_handle: Receipt handle from the SQS event record.

        Raises:
            QueueServiceException: If the SQS delete_message call fails.
        """
        logger.info(
            "Deleting SQS message. queue_url=%s receipt_handle=%.40s...",
            queue_url,
            receipt_handle,
        )
        try:
            self._client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )
        except ClientError as exc:
            logger.error(
                "SQS delete_message failed. queue_url=%s error=%s",
                queue_url,
                str(exc),
            )
            raise QueueServiceException(
                "Failed to delete SQS message after processing."
            ) from exc

        logger.info(
            "SQS message deleted successfully. queue_url=%s", queue_url
        )

    def get_queue_attributes(self, queue_url: str) -> dict[str, Any]:
        """
        Retrieve queue attributes (e.g., ApproximateNumberOfMessages) for monitoring.

        Args:
            queue_url: Full URL of the SQS queue.

        Returns:
            dict of queue attribute names to values.

        Raises:
            QueueServiceException: If the SQS call fails.
        """
        logger.info("Fetching SQS queue attributes. queue_url=%s", queue_url)
        try:
            response: dict[str, Any] = self._client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=["All"],
            )
        except ClientError as exc:
            logger.error(
                "SQS get_queue_attributes failed. queue_url=%s error=%s",
                queue_url,
                str(exc),
            )
            raise QueueServiceException(
                "Failed to retrieve SQS queue attributes."
            ) from exc

        attributes: dict[str, Any] = response.get("Attributes", {})
        logger.info(
            "SQS attributes fetched. queue_url=%s attributes=%s",
            queue_url,
            attributes,
        )
        return attributes
