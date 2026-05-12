"""
handler.py (processing_lambda)

AWS Lambda entry point for the asynchronous invoice processing pipeline.

Trigger: SQS queue (S3 → SQS event notification → this Lambda)

Event structure (SQS wrapping S3 notification):
    {
        "Records": [
            {
                "body": "{... S3 event JSON ...}",
                "receiptHandle": "...",
                "eventSourceARN": "arn:aws:sqs:..."
            },
            ...
        ]
    }

Processing pipeline per SQS record:
    1. Extract bucket_name + file_key from the S3 event embedded in the SQS message body.
    2. Call textract_service.analyze_document() → raw Textract blocks.
    3. Call invoice_parser.parse()              → structured Invoice model.
    4. Call summary_service.generate_summary()  → human-readable summary string.
    5. Attach summary to Invoice.
    6. Call dynamodb_service.save_invoice()     → persist to DynamoDB.

Error handling:
    - Per-record errors are logged at ERROR level and do NOT suppress processing
      of remaining records in the batch.
    - If all records fail, the function raises to trigger SQS retry / DLQ.
    - TextractProcessingException, InvoiceParsingException, DynamoDBException
      are all caught individually so the log message is precise.
"""

import json
import logging
import os
from typing import Any

from processing_lambda.exceptions.custom_exceptions import (
    DynamoDBException,
    InvoiceParsingException,
    TextractProcessingException,
)
from processing_lambda.models.invoice import Invoice
from processing_lambda.parsers.invoice_parser import InvoiceParser
from processing_lambda.services.dynamodb_service import DynamoDBService
from processing_lambda.services.summary_service import SummaryService
from processing_lambda.services.textract_service import TextractService
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level service singletons — instantiated once per cold start
# ---------------------------------------------------------------------------

_textract_service = TextractService()
_invoice_parser = InvoiceParser()
_summary_service = SummaryService()
_dynamodb_service = DynamoDBService()


# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Process a batch of SQS records, each containing an S3 event notification.

    AWS Lambda automatically deletes SQS messages on successful handler return.
    Failed records can be configured to flow to a Dead Letter Queue via the
    SQS event source mapping's function response type.

    Args:
        event:   SQS event dict with a 'Records' list.
        context: Lambda runtime context (used for request_id logging).

    Returns:
        dict reporting the number of successfully processed records.

    Raises:
        RuntimeError: If every record in the batch fails processing,
                      to signal Lambda to return messages to SQS for retry.
    """
    request_id: str = getattr(context, "aws_request_id", "local")
    records: list[dict[str, Any]] = event.get("Records", [])

    logger.info(
        "Processing Lambda invoked. request_id=%s record_count=%d",
        request_id,
        len(records),
    )

    success_count: int = 0
    failure_count: int = 0

    for idx, record in enumerate(records):
        logger.info(
            "Processing SQS record. request_id=%s record_index=%d",
            request_id,
            idx,
        )
        try:
            _process_record(record)
            success_count += 1
            logger.info(
                "SQS record processed successfully. request_id=%s record_index=%d",
                request_id,
                idx,
            )
        except (
            TextractProcessingException,
            InvoiceParsingException,
            DynamoDBException,
        ) as exc:
            failure_count += 1
            logger.error(
                "Known processing error for record. request_id=%s "
                "record_index=%d error_type=%s error=%s",
                request_id,
                idx,
                type(exc).__name__,
                str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            failure_count += 1
            logger.error(
                "Unexpected error for record. request_id=%s "
                "record_index=%d error=%s",
                request_id,
                idx,
                str(exc),
            )

    logger.info(
        "Batch complete. request_id=%s success=%d failure=%d",
        request_id,
        success_count,
        failure_count,
    )

    if failure_count > 0 and success_count == 0:
        raise RuntimeError(
            f"All {failure_count} record(s) failed processing. "
            "Returning batch to SQS for retry."
        )

    return {
        "statusCode": 200,
        "processed": success_count,
        "failed": failure_count,
    }


# ---------------------------------------------------------------------------
# Private: single-record processing pipeline
# ---------------------------------------------------------------------------


def _process_record(record: dict[str, Any]) -> None:
    """
    Execute the full processing pipeline for a single SQS record.

    Args:
        record: A single element from event['Records'].

    Raises:
        TextractProcessingException: If Textract analysis fails.
        InvoiceParsingException:     If parser cannot extract data from blocks.
        DynamoDBException:           If DynamoDB write fails.
        ValueError:                  If the SQS/S3 event structure is unexpected.
    """
    # Step 1: Extract S3 coordinates from SQS message body
    bucket_name, file_key = _extract_s3_coordinates(record)
    logger.info(
        "Extracted S3 coordinates. bucket=%s key=%s", bucket_name, file_key
    )

    # Step 2: Analyse document with Textract
    logger.info("Calling Textract. bucket=%s key=%s", bucket_name, file_key)
    blocks: list[dict[str, Any]] = _textract_service.analyze_document(
        bucket_name=bucket_name,
        file_key=file_key,
    )

    # Step 3: Parse Textract blocks into structured Invoice
    logger.info("Parsing Textract blocks. bucket=%s key=%s", bucket_name, file_key)
    invoice: Invoice = _invoice_parser.parse(
        blocks=blocks,
        bucket_name=bucket_name,
        file_key=file_key,
    )

    # Step 4: Generate human-readable summary
    logger.info(
        "Generating summary. invoice_id=%s", invoice.invoice_id
    )
    summary: str = _summary_service.generate_summary(invoice)
    invoice.summary = summary

    # Step 5: Persist to DynamoDB
    logger.info(
        "Saving invoice to DynamoDB. invoice_id=%s", invoice.invoice_id
    )
    _dynamodb_service.save_invoice(invoice)

    logger.info(
        "Pipeline complete. invoice_id=%s bucket=%s key=%s",
        invoice.invoice_id,
        bucket_name,
        file_key,
    )


def _extract_s3_coordinates(record: dict[str, Any]) -> tuple[str, str]:
    """
    Extract the S3 bucket name and object key from an SQS record.

    SQS wraps the S3 event as a JSON string in record['body'].
    The S3 event contains a list of S3 records under 's3'.

    Expected body structure:
        {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "my-bucket"},
                        "object": {"key": "uploads/uuid_invoice.pdf"}
                    }
                }
            ]
        }

    Args:
        record: A single SQS event record dict.

    Returns:
        Tuple of (bucket_name, file_key).

    Raises:
        ValueError: If the expected S3 event structure is missing or malformed.
    """
    try:
        body: dict[str, Any] = json.loads(record.get("body", "{}"))
        s3_records: list[dict[str, Any]] = body.get("Records", [])

        if not s3_records:
            raise ValueError(
                "SQS message body contains no S3 event records. "
                f"body={json.dumps(body)}"
            )

        s3_info: dict[str, Any] = s3_records[0].get("s3", {})
        bucket_name: str = s3_info.get("bucket", {}).get("name", "")
        file_key: str = s3_info.get("object", {}).get("key", "")

        if not bucket_name or not file_key:
            raise ValueError(
                f"Missing bucket or key in S3 event. bucket={bucket_name!r} "
                f"key={file_key!r}"
            )

        # URL-decode the key (S3 encodes spaces as '+' or '%20')
        from urllib.parse import unquote_plus  # noqa: PLC0415
        file_key = unquote_plus(file_key)

        return bucket_name, file_key

    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.error(
            "Failed to extract S3 coordinates from SQS record. error=%s", str(exc)
        )
        raise ValueError(
            f"Malformed SQS/S3 event structure: {str(exc)}"
        ) from exc
