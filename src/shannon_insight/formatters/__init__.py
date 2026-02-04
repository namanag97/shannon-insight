"""Output formatters for Shannon Insight."""

from .base import BaseFormatter
from .rich_formatter import RichFormatter
from .json_formatter import JsonFormatter
from .csv_formatter import CsvFormatter
from .quiet_formatter import QuietFormatter
from .diff_formatter import DiffFormatter
from .github_formatter import GithubFormatter


def get_formatter(name: str) -> BaseFormatter:
    """Get a formatter instance by name.

    Args:
        name: One of "rich", "json", "csv", "quiet", "github"

    Returns:
        Formatter instance

    Raises:
        ValueError: If name is not recognized
    """
    formatters = {
        "rich": RichFormatter,
        "json": JsonFormatter,
        "csv": CsvFormatter,
        "quiet": QuietFormatter,
        "github": GithubFormatter,
    }
    cls = formatters.get(name)
    if cls is None:
        raise ValueError(f"Unknown formatter: {name!r}. Choose from: {', '.join(sorted(formatters))}")
    return cls()


__all__ = [
    "BaseFormatter",
    "RichFormatter",
    "JsonFormatter",
    "CsvFormatter",
    "QuietFormatter",
    "DiffFormatter",
    "GithubFormatter",
    "get_formatter",
]
