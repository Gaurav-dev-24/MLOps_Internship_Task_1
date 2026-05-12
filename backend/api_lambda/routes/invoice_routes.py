"""
routes/invoice_routes.py (api_lambda)

FastAPI route handlers for the invoice API.

Responsibilities (ONLY):
  - Receive and validate the incoming HTTP request (via Pydantic schema).
  - Call the appropriate InvoiceService method.
  - Return a standardised response envelope via response_formatter.

Rules enforced here:
  - Zero business logic.
  - Zero boto3 / AWS SDK imports.
  - All success and error responses go through response_formatter helpers.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from exceptions.custom_exceptions import (
    DynamoDBException,
    InvoiceNotFoundException,
    S3UploadException,
)
from schemas.invoice_schema import UploadRequest
from services.invoice_service import InvoiceService
from utils.logger import get_logger
from utils.response_formatter import error_response, success_response

logger: logging.Logger = get_logger(__name__)

router = APIRouter()
_invoice_service = InvoiceService()


# ---------------------------------------------------------------------------
# POST /generate-upload-url
# ---------------------------------------------------------------------------


@router.post(
    "/generate-upload-url",
    summary="Generate a presigned S3 upload URL",
    response_description="Presigned URL and S3 file key",
    status_code=status.HTTP_200_OK,
)
def generate_upload_url(request: UploadRequest) -> dict[str, Any]:
    logger.info(
        "POST /generate-upload-url called. file_name=%s file_size=%d",
        request.file_name,
        request.file_size,
    )
    try:
        data: dict[str, str] = _invoice_service.create_upload_url(
            file_name=request.file_name
        )
        logger.info("Upload URL generated. file_key=%s", data.get("file_key"))
        return success_response(
            message="Upload URL generated successfully.", data=data
        )

    except S3UploadException as exc:
        logger.error("S3UploadException in generate_upload_url. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                message="Failed to generate upload URL.",
                error=str(exc),
            ),
        )

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error in generate_upload_url. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="An unexpected error occurred.",
                error=str(exc),
            ),
        )


# ---------------------------------------------------------------------------
# GET /invoices/stats  ← NEW
# ---------------------------------------------------------------------------


@router.get(
    "/invoices/stats",
    summary="Get invoice statistics",
    response_description="Aggregated invoice stats",
    status_code=status.HTTP_200_OK,
)
def get_invoice_stats() -> dict[str, Any]:
    """
    Return aggregated statistics over all invoice records.

    Returns:
        Success envelope containing total, processed, failed,
        pending counts and totalAmount.
    """
    logger.info("GET /invoices/stats called.")
    try:
        data: dict[str, Any] = _invoice_service.get_all_invoices()
        invoices = data.get("invoices", [])

        stats = {
            "total": len(invoices),
            "processed": len([i for i in invoices if i.get("status") == "processed"]),
            "failed": len([i for i in invoices if i.get("status") == "failed"]),
            "pending": len([i for i in invoices if i.get("status") == "pending"]),
            "totalAmount": sum(
                float(i.get("total_amount", 0)) for i in invoices
            ),
        }
        return success_response(message="Stats fetched successfully.", data=stats)

    except DynamoDBException as exc:
        logger.error("DynamoDBException in get_invoice_stats. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                message="Failed to fetch invoice stats.",
                error=str(exc),
            ),
        )

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error in get_invoice_stats. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="An unexpected error occurred.",
                error=str(exc),
            ),
        )


# ---------------------------------------------------------------------------
# GET /invoice/{invoice_id}
# ---------------------------------------------------------------------------


@router.get(
    "/invoice/{invoice_id}",
    summary="Get a single invoice by ID",
    response_description="Full invoice record",
    status_code=status.HTTP_200_OK,
)
def get_invoice(invoice_id: str) -> dict[str, Any]:
    logger.info("GET /invoice/%s called.", invoice_id)
    try:
        data: dict[str, Any] = _invoice_service.get_invoice(invoice_id)
        logger.info("Invoice fetched successfully. invoice_id=%s", invoice_id)
        return success_response(message="Invoice fetched successfully.", data=data)

    except InvoiceNotFoundException as exc:
        logger.info("Invoice not found. invoice_id=%s", invoice_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                message="Invoice not found.",
                error=str(exc),
            ),
        )

    except DynamoDBException as exc:
        logger.error(
            "DynamoDBException in get_invoice. invoice_id=%s error=%s",
            invoice_id,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                message="Failed to retrieve invoice from database.",
                error=str(exc),
            ),
        )

    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in get_invoice. invoice_id=%s error=%s",
            invoice_id,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="An unexpected error occurred.",
                error=str(exc),
            ),
        )


# ---------------------------------------------------------------------------
# GET /invoices
# ---------------------------------------------------------------------------


@router.get(
    "/invoices",
    summary="List all invoices",
    response_description="Array of all invoice records",
    status_code=status.HTTP_200_OK,
)
def get_all_invoices() -> dict[str, Any]:
    logger.info("GET /invoices called.")
    try:
        data: dict[str, Any] = _invoice_service.get_all_invoices()
        logger.info(
            "All invoices fetched successfully. total=%d",
            len(data.get("invoices", [])),
        )
        return success_response(message="Invoices fetched successfully.", data=data)

    except DynamoDBException as exc:
        logger.error("DynamoDBException in get_all_invoices. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                message="Failed to retrieve invoices from database.",
                error=str(exc),
            ),
        )

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error in get_all_invoices. error=%s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="An unexpected error occurred.",
                error=str(exc),
            ),
        )