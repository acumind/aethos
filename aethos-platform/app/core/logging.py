import logging
import sys
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    LOGGING_LEVEL: str = "INFO"
    # Format for logs
    LOGGING_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    Intercepts all standard library logging and redirects to loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding loguru level if exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Setup logging configuration.

    Intercepts standard library logging and redirects to loguru.
    Also configures loguru handlers.
    """
    config = LoggingConfig()

    # Remove default handlers
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(config.LOGGING_LEVEL)

    # Remove all existing loguru handlers
    logger.remove()

    # Configure loguru to stdout
    logger.configure(
        handlers=[{"sink": sys.stdout, "format": config.LOGGING_FORMAT,
                   "level": config.LOGGING_LEVEL}]
    )

    # Redirect standard library logging
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Set level for specific libraries as needed
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
