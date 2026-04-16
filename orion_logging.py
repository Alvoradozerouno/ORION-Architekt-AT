"""
Logging Infrastructure for ORION Architekt-AT

Provides centralized logging with proper configuration for production,
development, and testing environments.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import json

# Default log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# Custom JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "bundesland"):
            log_data["bundesland"] = record.bundesland
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        return json.dumps(log_data, ensure_ascii=False)


# Logging configuration
def setup_logging(
    level=logging.INFO,
    log_file=None,
    console=True,
    json_format=False,
    max_bytes=10485760,  # 10MB
    backup_count=5,
):
    """
    Setup logging configuration for ORION Architekt-AT.

    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
        console: Whether to log to console (default: True)
        json_format: Use JSON formatting (default: False)
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        logging.Logger: Configured root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Format
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


# Module-specific loggers
def get_logger(name):
    """
    Get a logger for a specific module.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


# Predefined log levels for different components
LOGGER_CONFIGS = {
    "orion_architekt_at": {"level": logging.INFO},
    "orion_kb_validation": {"level": logging.INFO},
    "orion_agent_core": {"level": logging.DEBUG},
    "tests": {"level": logging.WARNING},
}


def configure_module_loggers():
    """Configure logging levels for specific modules"""
    for module_name, config in LOGGER_CONFIGS.items():
        logger = logging.getLogger(module_name)
        logger.setLevel(config["level"])


# Context manager for logging context
class LogContext:
    """Add context to logs within a block"""

    def __init__(self, **kwargs):
        self.context = kwargs
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


# Convenience functions for common logging patterns


def log_calculation(logger, calc_type, input_data, result):
    """Log a calculation with input and output"""
    logger.info(
        f"Berechnung: {calc_type}",
        extra={"calculation_type": calc_type, "input": input_data, "result": result},
    )


def log_compliance_check(logger, check_type, bundesland, result):
    """Log a compliance check"""
    logger.info(
        f"Compliance-Check: {check_type} für {bundesland}",
        extra={
            "check_type": check_type,
            "bundesland": bundesland,
            "passed": result.get("erfuellt", False),
        },
    )


def log_validation(logger, validation_type, status, details=None):
    """Log a validation result"""
    logger.info(
        f"Validierung: {validation_type} - Status: {status}",
        extra={"validation_type": validation_type, "status": status, "details": details},
    )


def log_error(logger, error_type, error_message, **kwargs):
    """Log an error with context"""
    logger.error(
        f"Error: {error_type} - {error_message}",
        extra={"error_type": error_type, "error_message": error_message, **kwargs},
        exc_info=True,
    )


# Default setup for ORION Architekt-AT
def setup_default_logging():
    """Setup default logging configuration"""
    # Main application log
    setup_logging(
        level=logging.INFO,
        log_file=LOG_DIR / f"orion_architekt_{datetime.now().strftime('%Y%m%d')}.log",
        console=True,
        json_format=False,
    )

    # Configure module loggers
    configure_module_loggers()

    # Log startup
    logger = get_logger(__name__)
    logger.info("ORION Architekt-AT Logging initialized")


# Performance logging decorator
def log_performance(logger):
    """Decorator to log function execution time"""
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(
                    f"Function {func.__name__} completed in {elapsed:.3f}s",
                    extra={"function": func.__name__, "elapsed_seconds": elapsed, "success": True},
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Function {func.__name__} failed after {elapsed:.3f}s: {e}",
                    extra={
                        "function": func.__name__,
                        "elapsed_seconds": elapsed,
                        "success": False,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_default_logging()

    logger = get_logger("example")

    # Basic logging
    logger.info("Starting ORION Architekt-AT")
    logger.debug("Debug message")
    logger.warning("Warning message")

    # Context logging
    with LogContext(bundesland="tirol", user_id="user123"):
        logger.info("Processing for Tirol")

    # Performance logging
    @log_performance(logger)
    def slow_calculation():
        import time

        time.sleep(0.1)
        return 42

    result = slow_calculation()

    logger.info("ORION Architekt-AT completed successfully")
