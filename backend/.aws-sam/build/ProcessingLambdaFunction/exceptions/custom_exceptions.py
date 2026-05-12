"""
exceptions/custom_exceptions.py (processing_lambda)

Custom exception hierarchy for the processing_lambda package.
Every boto3 ClientError in the processing pipeline must be caught and
re-raised as one of these to maintain clear error boundaries between
Textract, DynamoDB, and SQS operations.
"""


class TextractProcessingException(Exception):
    """
    Raised when AWS Textract fails to analyse a document.

    Wraps botocore.exceptions.ClientError from textract_service calls.
    """

    pass


class DynamoDBException(Exception):
    """
    Raised when a DynamoDB write operation fails inside processing_lambda.

    Wraps botocore.exceptions.ClientError raised by boto3 DynamoDB resource calls.
    """

    pass


class InvoiceParsingException(Exception):
    """
    Raised when invoice_parser cannot extract meaningful data from
    the Textract response blocks.

    This is a domain-level exception, not an AWS error.
    """

    pass


class QueueServiceException(Exception):
    """
    Raised when an SQS operation fails inside processing_lambda.

    Wraps botocore.exceptions.ClientError from SQS client calls.
    """

    pass
