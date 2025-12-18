"""
Logging configuration for GitaBae.

Provides consistent logging across all modules with proper formatting,
log levels, and optional file output.

Usage:
    from src.logger import get_logger
    logger = get_logger(__name__)

    logger.info("Processing started")
    logger.warning("Low relevance score")
    logger.error("Failed to connect", exc_info=True)
"""

import logging
import sys
from typing import Optional


# Default format for all loggers
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(levelname)s - %(message)s"


def get_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    use_simple_format: bool = False
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        use_simple_format: Use simplified format without timestamps

    Returns:
        Configured logging.Logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("User query received")
        logger.error("API call failed", exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if logger already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Determine format string
        if format_string is None:
            format_string = SIMPLE_FORMAT if use_simple_format else DEFAULT_FORMAT

        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def configure_root_logger(level: int = logging.INFO) -> None:
    """
    Configure the root logger for the application.

    Call this once at application startup to set default logging behavior.

    Args:
        level: Default logging level for the application
    """
    logging.basicConfig(
        level=level,
        format=DEFAULT_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


# =============================================================================
# PRE-CONFIGURED LOGGERS FOR COMMON MODULES
# =============================================================================

def get_app_logger() -> logging.Logger:
    """Get logger for main Streamlit app."""
    return get_logger("gitabae.app")


def get_generator_logger() -> logging.Logger:
    """Get logger for response generation."""
    return get_logger("gitabae.generator")


def get_retriever_logger() -> logging.Logger:
    """Get logger for verse retrieval."""
    return get_logger("gitabae.retriever")


def get_safety_logger() -> logging.Logger:
    """Get logger for safety checks."""
    return get_logger("gitabae.safety")


def get_feedback_logger() -> logging.Logger:
    """Get logger for feedback system."""
    return get_logger("gitabae.feedback")


def get_vectorstore_logger() -> logging.Logger:
    """Get logger for vector store operations."""
    return get_logger("gitabae.vectorstore")


def get_embeddings_logger() -> logging.Logger:
    """Get logger for embeddings generation."""
    return get_logger("gitabae.embeddings")


# =============================================================================
# USAGE EXAMPLES (for documentation)
# =============================================================================

if __name__ == "__main__":
    # Demo logging at different levels
    logger = get_logger("demo", level=logging.DEBUG)

    logger.debug("This is a debug message - detailed info for developers")
    logger.info("This is an info message - general operational info")
    logger.warning("This is a warning - something unexpected but not critical")
    logger.error("This is an error - something failed")

    # With exception info
    try:
        raise ValueError("Example error")
    except Exception:
        logger.error("Caught an exception", exc_info=True)
