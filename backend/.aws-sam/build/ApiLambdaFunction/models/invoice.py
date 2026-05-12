"""
models/invoice.py (api_lambda)

Internal domain model representing a fully-processed invoice record
as stored in DynamoDB. This is a pure Python dataclass — no Pydantic,
no boto3. It is used to carry data between the repository and the service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineItem:
    """A single line item extracted from an invoice."""

    description: str = ""
    quantity: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class Invoice:
    """
    Domain model for an invoice record.

    Maps 1-to-1 with the DynamoDB InvoicesTable schema.
    Numeric fields (tax_amount, total_amount) are stored as strings
    to preserve exact decimal representation from Textract.
    """

    invoice_id: str
    vendor_name: str = ""
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

    @classmethod
    def from_dynamo_item(cls, item: dict[str, Any]) -> "Invoice":
        """
        Construct an Invoice from a raw DynamoDB get_item / scan response item.

        DynamoDB returns all values as strings or Decimal; we normalise
        everything to str here so callers never need to handle Decimal.

        Args:
            item: Raw dict from a DynamoDB response['Item'] or response['Items'][n].

        Returns:
            Populated Invoice dataclass instance.
        """
        raw_items: list[dict[str, Any]] = item.get("line_items", [])
        line_items: list[LineItem] = [
            LineItem(
                description=str(li.get("description", "")),
                quantity=str(li.get("quantity", "")),
                unit_price=str(li.get("unit_price", "")),
                amount=str(li.get("amount", "")),
            )
            for li in raw_items
        ]

        return cls(
            invoice_id=str(item.get("invoice_id", "")),
            vendor_name=str(item.get("vendor_name", "")),
            invoice_date=str(item.get("invoice_date", "")),
            due_date=str(item.get("due_date", "")),
            currency=str(item.get("currency", "")),
            tax_amount=str(item.get("tax_amount", "")),
            total_amount=str(item.get("total_amount", "")),
            line_items=line_items,
            extracted_json=item.get("extracted_json", {}),
            summary=str(item.get("summary", "")),
            s3_path=str(item.get("s3_path", "")),
            created_at=str(item.get("created_at", "")),
        )
