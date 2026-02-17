"""
Custom exception classes for the service.

Provides domain-specific exceptions with HTTP status codes for proper
error handling and client communication.
"""

from fastapi import HTTPException, status


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 400):
        """Initialize exception with message and HTTP status code."""
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        """Initialize with 422 status code."""
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize with 401 status code."""
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Insufficient permissions"):
        """Initialize with 403 status code."""
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """Raised when resource is not found."""

    def __init__(self, resource: str, identifier: str):
        """Initialize with 404 status code."""
        message = f"{resource} not found: {identifier}"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Raised when resource already exists."""

    def __init__(self, message: str):
        """Initialize with 409 status code."""
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class InternalServerError(AppException):
    """Raised for internal server errors."""

    def __init__(self, message: str = "Internal server error"):
        """Initialize with 500 status code."""
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def to_http_exception(exc: AppException) -> HTTPException:
    """Convert AppException to FastAPI HTTPException."""
    return HTTPException(status_code=exc.status_code, detail=exc.message)


# Fix for edge case in error handling
# Fix for edge case in error handling
