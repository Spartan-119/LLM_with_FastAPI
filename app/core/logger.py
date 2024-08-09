import json
import logging
import os
from logging import handlers
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

# Create a logger
logger = logging.getLogger("llm_hub")
logger.setLevel(logging.DEBUG)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for logging that adds timestamp and uppercase level.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
)
logger.addHandler(console_handler)

# Create file handler if logs directory exists
logs_dir = os.path.join(os.getcwd(), "logs")
if os.path.exists(logs_dir):
    file_handler = handlers.RotatingFileHandler(
        os.path.join(logs_dir, "llm_hub.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(
        CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    )
    logger.addHandler(file_handler)


def log_error(error: Exception, **kwargs: Any) -> None:
    """
    Log an error with additional context.

    Args:
        error (Exception): The exception to log.
        **kwargs: Additional key-value pairs to include in the log.
    """
    logger.error(
        json.dumps(
            {"error_type": type(error).__name__, "error_message": str(error), **kwargs}
        )
    )


def log_info(message: str, **kwargs: Any) -> None:
    """
    Log an info message with additional context.

    Args:
        message (str): The main log message.
        **kwargs: Additional key-value pairs to include in the log.
    """
    logger.info(json.dumps({"message": message, **kwargs}))


def configure_logger(log_level: str = "INFO") -> None:
    """
    Configure the logger with the specified log level.

    Args:
        log_level (str): The desired log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    logger.setLevel(getattr(logging, log_level.upper()))


# Example usage of configure_logger:
# configure_logger("DEBUG")  # Set this based on your environment or configuration
