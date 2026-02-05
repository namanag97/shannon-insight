"""Base exception for Shannon Insight."""

from typing import Dict, Optional


class ShannonInsightError(Exception):
    """Base exception for all Shannon Insight errors."""

    def __init__(self, message: str, details: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message
