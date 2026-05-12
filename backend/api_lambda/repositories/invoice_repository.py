"""
repositories/invoice_repository.py (api_lambda)

DynamoDB data-access layer for invoice records.

Responsibilities:
  - get_by_id  : fetch a single invoice by primary key
  - get_all    : full table scan (suitable for MVP; replace with GSI + query for scale)

This file must NOT contain any business logic.
All returned objects are Invoice domain model instances.
"""

import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from config.settings import settings
from exceptions.custom_exceptions import DynamoDBException, InvoiceNotFoundException
from models.invoice import Invoice
from utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)


class InvoiceRepository:
    """Abstracts all DynamoDB read operations for the InvoicesTable."""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        self._table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

    def get_by_id(self, invoice_id: str) -> Invoice:
        """
        Retrieve a single invoice record from DynamoDB by primary key.

        Args:
            invoice_id: The partition key value to look up.

        Returns:
            Invoice domain model populated from the DynamoDB item.

        Raises:
            InvoiceNotFoundException: If no item exists for the given invoice_id.
            DynamoDBException: If the DynamoDB API call fails.
        """
        logger.info("Fetching invoice from DynamoDB. invoice_id=%s", invoice_id)
        try:
            response: dict[str, Any] = self._table.get_item(
                Key={"invoice_id": invoice_id}
            )
        except ClientError as exc:
            logger.error(
                "DynamoDB get_item failed. invoice_id=%s error=%s",
                invoice_id,
                str(exc),
            )
            raise DynamoDBException(
                f"Failed to fetch invoice '{invoice_id}' from DynamoDB."
            ) from exc

        item: dict[str, Any] | None = response.get("Item")
        if not item:
            logger.info("Invoice not found. invoice_id=%s", invoice_id)
            raise InvoiceNotFoundException(
                f"Invoice with id '{invoice_id}' was not found."
            )

        invoice: Invoice = Invoice.from_dynamo_item(item)
        logger.info("Invoice fetched successfully. invoice_id=%s", invoice_id)
        return invoice

    def get_all(self) -> list[Invoice]:
        """
        Retrieve all invoice records from DynamoDB using a full table scan.

        NOTE: For production at scale, replace with a GSI + query to avoid
        consuming excessive read capacity on large tables.

        Returns:
            List of Invoice domain model instances (may be empty).

        Raises:
            DynamoDBException: If the DynamoDB API call fails.
        """
        logger.info("Scanning DynamoDB table for all invoices.")
        try:
            response: dict[str, Any] = self._table.scan()
        except ClientError as exc:
            logger.error("DynamoDB scan failed. error=%s", str(exc))
            raise DynamoDBException(
                "Failed to retrieve invoices from DynamoDB."
            ) from exc

        items: list[dict[str, Any]] = response.get("Items", [])

        # Handle DynamoDB pagination — keep scanning while LastEvaluatedKey exists
        while "LastEvaluatedKey" in response:
            logger.info(
                "DynamoDB scan paginating. fetched_so_far=%d", len(items)
            )
            try:
                response = self._table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
            except ClientError as exc:
                logger.error(
                    "DynamoDB paginated scan failed. error=%s", str(exc)
                )
                raise DynamoDBException(
                    "Failed to paginate invoices from DynamoDB."
                ) from exc
            items.extend(response.get("Items", []))

        invoices: list[Invoice] = [Invoice.from_dynamo_item(item) for item in items]
        logger.info("All invoices fetched successfully. total=%d", len(invoices))
        return invoices
