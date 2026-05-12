"""
schemas/invoice_schema.py (api_lambda)

Pydantic v2 request/response schemas for the invoice API.

Validation rules enforced here before any service call is made:
  - file_name extension must be in the allowed list
  - file_size must not exceed the configured maximum (10 MB default)

These schemas are the only place where input validation logic lives.
Routes receive a validated schema instance; services receive plain data.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from api_lambda.config.settings import settings


class UploadRequest(BaseModel):
    """
    Request body for POST /generate-upload-url.

    Validates file extension and file size before the service is called.
    """

    file_name: str = Field(
        ...,
        min_length=1,
        description="Original filename including extension (e.g. invoice.pdf)",
    )
    file_size: int = Field(
        ...,
        gt=0,
        description="File size in bytes. Must be > 0 and <= MAX_FILE_SIZE_BYTES.",
    )

    @field_validator("file_name")
    @classmethod
    def validate_extension(cls, value: str) -> str:
        """Reject files whose extension is not in the allowed list."""
        ext: str = os.path.splitext(value)[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File extension '{ext}' is not allowed. "
                f"Accepted: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        return value

    @field_validator("file_size")
    @classmethod
    def validate_size(cls, value: int) -> int:
        """Reject files that exceed the configured size limit."""
        if value > settings.MAX_FILE_SIZE_BYTES:
            max_mb: float = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise ValueError(
                f"File size {value} bytes exceeds the maximum allowed "
                f"size of {max_mb:.0f} MB ({settings.MAX_FILE_SIZE_BYTES} bytes)."
            )
        return value


class UploadUrlResponse(BaseModel):
    """Payload returned inside data for POST /generate-upload-url."""

    upload_url: str
    file_key: str


class LineItemResponse(BaseModel):
    """A single line item inside an InvoiceResponse."""

    description: str = ""
    quantity: str = ""
    unit_price: str = ""
    amount: str = ""


class InvoiceResponse(BaseModel):
    """
    Payload returned inside data for GET /invoice/{invoice_id}
    and each element in GET /invoices.
    """

    invoice_id: str
    vendor_name: str = ""
    invoice_date: str = ""
    due_date: str = ""
    currency: str = ""
    tax_amount: str = ""
    total_amount: str = ""
    line_items: list[LineItemResponse] = Field(default_factory=list)
    extracted_json: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""
    s3_path: str = ""
    created_at: str = ""

    model_config = {"from_attributes": True}
