"""
services/dynamodb_service.py (processing_lambda)

DynamoDB write service for the processing pipeline.

Responsibilities:
  - Persist a fully-processed Invoice record to the InvoicesTable.
  - Wrap all ClientError exceptions as DynamoDBException.
"""

import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from processing_lambda.exceptions.custom_exceptions import DynamoDBException
from processing_lambda.models.invoice import Invoice
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

_AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")
_TABLE_NAME: str = os.environ.get("DYNAMODB_TABLE_NAME", "InvoicesTable")


class DynamoDBService:
    """Handles all DynamoDB write operations for the processing pipeline."""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=_AWS_REGION)
        self._table = dynamodb.Table(_TABLE_NAME)

    def save_invoice(self, invoice: Invoice) -> None:
        """
        Persist a processed invoice record to the DynamoDB InvoicesTable.

        Uses a conditional put to avoid overwriting an existing record with
        the same invoice_id (idempotency guard for SQS at-least-once delivery).
        If the item already exists, the condition fails silently and is logged
        as a warning rather than raised as an error.

        Args:
            invoice: Fully-populated Invoice domain model instance.

        Raises:
            DynamoDBException: If the put_item call fails for any reason
                               other than a ConditionalCheckFailedException.
        """
        item: dict[str, Any] = invoice.to_dynamo_item()
        logger.info(
            "Saving invoice to DynamoDB. invoice_id=%s table=%s",
            invoice.invoice_id,
            _TABLE_NAME,
        )
        try:
            self._table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(invoice_id)",
            )
        except ClientError as exc:
            error_code: str = exc.response.get("Error", {}).get("Code", "")
            if error_code == "ConditionalCheckFailedException":
                # Invoice already processed — idempotent, not an error
                logger.warning(
                    "Invoice already exists in DynamoDB, skipping duplicate write. "
                    "invoice_id=%s",
                    invoice.invoice_id,
                )
                return
            logger.error(
                "DynamoDB put_item failed. invoice_id=%s error=%s",
                invoice.invoice_id,
                str(exc),
            )
            raise DynamoDBException(
                f"Failed to save invoice '{invoice.invoice_id}' to DynamoDB."
            ) from exc

        logger.info(
            "Invoice saved successfully to DynamoDB. invoice_id=%s",
            invoice.invoice_id,
        )
