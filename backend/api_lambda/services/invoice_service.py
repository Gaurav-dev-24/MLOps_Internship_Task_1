"""
services/invoice_service.py (api_lambda)

Invoice orchestration service.

Responsibilities:
  - Coordinate between s3_service and invoice_repository.
  - Transform domain model objects into response dicts consumed by routes.

Routes call this service; this service calls s3_service / repository.
No boto3 imports here — AWS calls are encapsulated in the layers below.
"""

import logging
from typing import Any

from api_lambda.models.invoice import Invoice
from api_lambda.repositories.invoice_repository import InvoiceRepository
from api_lambda.services.s3_service import S3Service
from api_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)


class InvoiceService:
    """Orchestrates invoice upload URL generation and invoice retrieval."""

    def __init__(self) -> None:
        self._s3_service = S3Service()
        self._repository = InvoiceRepository()

    # ------------------------------------------------------------------
    # Upload URL
    # ------------------------------------------------------------------

    def create_upload_url(self, file_name: str) -> dict[str, str]:
        """
        Generate a presigned S3 PUT URL for direct client upload.

        Args:
            file_name: Validated original filename (extension already checked).

        Returns:
            dict with keys: upload_url, file_key.

        Raises:
            S3UploadException: Propagated from s3_service if URL generation fails.
        """
        logger.info(
            "Requesting presigned upload URL. file_name=%s", file_name
        )
        presigned_url, file_key = self._s3_service.generate_presigned_url(
            file_name
        )
        logger.info(
            "Upload URL ready. file_key=%s", file_key
        )
        return {"upload_url": presigned_url, "file_key": file_key}

    # ------------------------------------------------------------------
    # Single invoice retrieval
    # ------------------------------------------------------------------

    def get_invoice(self, invoice_id: str) -> dict[str, Any]:
        """
        Retrieve a single invoice record and serialise it for the API response.

        Args:
            invoice_id: DynamoDB primary key to look up.

        Returns:
            Serialised invoice dict matching InvoiceResponse schema.

        Raises:
            InvoiceNotFoundException: If no invoice exists for the given id.
            DynamoDBException: If the DynamoDB call fails.
        """
        logger.info("Fetching invoice. invoice_id=%s", invoice_id)
        invoice: Invoice = self._repository.get_by_id(invoice_id)
        serialised: dict[str, Any] = self._serialise_invoice(invoice)
        logger.info(
            "Invoice retrieved successfully. invoice_id=%s", invoice_id
        )
        return serialised

    # ------------------------------------------------------------------
    # All invoices retrieval
    # ------------------------------------------------------------------

    def get_all_invoices(self) -> dict[str, Any]:
        """
        Retrieve all invoice records and serialise them for the API response.

        Returns:
            dict with key 'invoices' containing a list of serialised invoice dicts.

        Raises:
            DynamoDBException: If the DynamoDB scan fails.
        """
        logger.info("Fetching all invoices.")
        invoices: list[Invoice] = self._repository.get_all()
        serialised_list: list[dict[str, Any]] = [
            self._serialise_invoice(inv) for inv in invoices
        ]
        logger.info(
            "All invoices retrieved successfully. total=%d", len(serialised_list)
        )
        return {"invoices": serialised_list}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialise_invoice(invoice: Invoice) -> dict[str, Any]:
        """Convert an Invoice domain model to a JSON-serialisable dict."""
        return {
            "invoice_id": invoice.invoice_id,
            "vendor_name": invoice.vendor_name,
            "invoice_date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "currency": invoice.currency,
            "tax_amount": invoice.tax_amount,
            "total_amount": invoice.total_amount,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": li.quantity,
                    "unit_price": li.unit_price,
                    "amount": li.amount,
                }
                for li in invoice.line_items
            ],
            "extracted_json": invoice.extracted_json,
            "summary": invoice.summary,
            "s3_path": invoice.s3_path,
            "created_at": invoice.created_at,
        }
