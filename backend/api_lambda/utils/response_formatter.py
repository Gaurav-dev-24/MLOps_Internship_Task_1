"""
utils/response_formatter.py

Shared response envelope factory for all api_lambda routes.
Every route must use these helpers — no ad-hoc dict construction in routes.

Success envelope:
    { "success": true, "message": "...", "data": {...} }

Error envelope:
    { "success": false, "message": "...", "error": "..." }
"""


def success_response(message: str, data: dict) -> dict:
    """
    Build a standardised success response envelope.

    Args:
        message: Human-readable description of the successful operation.
        data:    Payload to return to the client.

    Returns:
        dict with keys: success (True), message, data.
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, error: str) -> dict:
    """
    Build a standardised error response envelope.

    Args:
        message: Human-readable description of what went wrong.
        error:   Technical error detail or exception message.

    Returns:
        dict with keys: success (False), message, error.
    """
    return {
        "success": False,
        "message": message,
        "error": error,
    }
