"""Logging configuration for bill ingestion."""

import logging
import sys
from bill_ingestion.config import Config

LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)

def _build_handler(
    handler: logging.Handler,
    level: int,
    formatter: logging.Formatter,
) -> logging.Handler:
    """Apply level and formatter to a handler and return it."""
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def setup_logger(name: str, config: Config) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (usually __name__)
        config: Application configuration

    Returns:
        Configured logger instance
    """
    # Validate LOG_LEVEL before doing anything else
    level = logging.getLevelName(config.LOG_LEVEL)
    if not isinstance(level, int):
        raise ValueError(
            f"Invalid LOG_LEVEL '{config.LOG_LEVEL}'. "
            f"Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)
    log_file = config.LOGS_DIR / "bill_ingestion.log"

    console_handler = _build_handler(logging.StreamHandler(sys.stdout), level, formatter)
    file_handler = _build_handler(logging.FileHandler(log_file), level, formatter)

    # Add handlers to logger
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)    
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)

    return logger
