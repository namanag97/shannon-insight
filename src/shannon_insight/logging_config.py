"""
Logging configuration for Shannon Insight.

Provides structured logging with rich formatting for beautiful terminal output.
"""

import logging
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    verbose: bool = False, quiet: bool = False, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging with rich handler for colored output.

    Args:
        verbose: Enable DEBUG level logging
        quiet: Suppress all but ERROR level logging
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance for shannon_insight
    """
    # Determine log level
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    # Create rich console for logging
    console = Console(stderr=True)

    # Configure handlers
    handlers: list[logging.Handler] = [
        RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=verbose,
            markup=True,
            show_time=True,
            show_path=verbose,
        )
    ]

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, format="%(message)s", datefmt="[%X]", handlers=handlers)

    # Get shannon_insight logger
    logger = logging.getLogger("shannon_insight")
    logger.setLevel(level)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (e.g., 'shannon_insight.core')
              If None, returns the root shannon_insight logger

    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger("shannon_insight")

    # Ensure name starts with shannon_insight
    if not name.startswith("shannon_insight"):
        name = f"shannon_insight.{name}"

    return logging.getLogger(name)
