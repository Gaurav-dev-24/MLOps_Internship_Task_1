"""
models/invoice.py (processing_lambda)

Internal domain model used during the processing pipeline.
Mirrors the api_lambda model but lives here to keep each Lambda
fully self-contained without shared-package import complexity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineItem:
    """A single line item extracted from a Textract response."""

    description: str = ""
    quantity: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class Invoice:
    """
    Domain model for an invoice record produced by the processing pipeline.

    Built by invoice_parser.py from raw Textract blocks and then persisted
    to DynamoDB by dynamodb_service.py.
    """

    invoice_id: str
    vendor_name: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    due_date: str = ""
    currency: str = ""
    tax_amount: str = ""
    total_amount: str = ""
    line_items: list[LineItem] = field(default_factory=list)
    extracted_json: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    s3_path: str = ""
    created_at: str = ""

    def to_dynamo_item(self) -> dict[str, Any]:
        """
        Serialise the Invoice to a DynamoDB-compatible dict for put_item.

        Converts all LineItem dataclasses to plain dicts because DynamoDB
        cannot store Python dataclass instances directly.

        Returns:
            dict ready to pass as the Item argument to table.put_item().
        """
        return {
            "invoice_id": self.invoice_id,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "currency": self.currency,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": li.quantity,
                    "unit_price": li.unit_price,
                    "amount": li.amount,
                }
                for li in self.line_items
            ],
            "extracted_json": self.extracted_json,
            "summary": self.summary,
            "s3_path": self.s3_path,
            "created_at": self.created_at,
        }
