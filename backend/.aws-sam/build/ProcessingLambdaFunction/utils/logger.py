"""
utils/logger.py (processing_lambda)

Centralised logger factory for the processing_lambda package.
Identical pattern to api_lambda — Lambda stdout is captured by CloudWatch.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured Logger instance for the given module name.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A logging.Logger configured with a StreamHandler pointed at stdout.
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
