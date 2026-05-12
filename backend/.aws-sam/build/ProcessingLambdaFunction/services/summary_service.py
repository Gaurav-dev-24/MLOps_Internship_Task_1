"""
services/summary_service.py (processing_lambda)

Human-readable invoice summary generator.

Responsibilities:
  - Produce a plain-English summary string from structured invoice data.
  - This is intentionally kept separate from invoice_parser.py (SRP).

The summary format is:
    "Invoice from {vendor} dated {date}. Total {currency}{amount}.
     Contains {n} line item(s)."
"""

import logging

from processing_lambda.models.invoice import Invoice
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)


class SummaryService:
    """Generates human-readable summary strings from processed invoice data."""

    def generate_summary(self, invoice: Invoice) -> str:
        """
        Build a single human-readable summary sentence for an invoice.

        The summary is stored in DynamoDB alongside the structured data
        so the frontend can display it without any further processing.

        Args:
            invoice: Populated Invoice domain model (post-parsing).

        Returns:
            A plain-English summary string. Never raises — falls back to
            generic text if key fields are missing.
        """
        logger.info(
            "Generating summary for invoice. invoice_id=%s", invoice.invoice_id
        )

        vendor: str = invoice.vendor_name or "Unknown Vendor"
        date: str = invoice.invoice_date or "an unknown date"
        currency: str = invoice.currency or ""
        amount: str = invoice.total_amount or "0.00"
        item_count: int = len(invoice.line_items)
        item_word: str = "item" if item_count == 1 else "items"

        summary: str = (
            f"Invoice from {vendor} dated {date}. "
            f"Total {currency}{amount}. "
            f"Contains {item_count} line {item_word}."
        )

        logger.info(
            "Summary generated successfully. invoice_id=%s summary=%r",
            invoice.invoice_id,
            summary,
        )
        return summary
