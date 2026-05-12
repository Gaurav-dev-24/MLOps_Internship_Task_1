"""
exceptions/custom_exceptions.py (api_lambda)

Custom exception hierarchy for the api_lambda package.
Every boto3 ClientError must be caught and re-raised as one of these
so that routes can handle them uniformly without leaking AWS internals.
"""


class S3UploadException(Exception):
    """
    Raised when any S3 presigned-URL generation or S3 operation fails.

    Wraps botocore.exceptions.ClientError raised by boto3 S3 client calls.
    """

    pass


class DynamoDBException(Exception):
    """
    Raised when any DynamoDB read operation fails inside api_lambda.

    Wraps botocore.exceptions.ClientError raised by boto3 DynamoDB resource calls.
    """

    pass


class InvoiceNotFoundException(Exception):
    """
    Raised when a requested invoice_id does not exist in DynamoDB.

    This is a domain-level exception — not an AWS error — so it maps
    to HTTP 404 in the route handler.
    """

    pass
