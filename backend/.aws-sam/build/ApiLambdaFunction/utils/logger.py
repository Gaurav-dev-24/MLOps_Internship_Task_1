"""
utils/logger.py (api_lambda)

Centralised logger factory for the api_lambda package.
Every module should call get_logger(__name__) to obtain a namespaced logger
that routes output to CloudWatch via Lambda's stdout capture.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured Logger instance for the given module name.

    CloudWatch Logs captures everything written to stdout/stderr by Lambda,
    so we simply stream to stdout with a structured format string.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A logging.Logger configured with a StreamHandler.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
