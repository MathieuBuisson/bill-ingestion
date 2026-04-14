"""Logging configuration for bill ingestion."""

import logging
import sys
from pathlib import Path
from bill_ingestion.config import Config

def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    config = Config()
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.LOG_LEVEL)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File handler
    log_file = config.LOGS_DIR / "bill_ingestion.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(config.LOG_LEVEL)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger