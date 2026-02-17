"""
FastAPI middleware for authentication, logging, and request handling.

Implements cross-cutting concerns like request tracing and structured logging.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(exc)}",
                extra={"request_id": request_id, "duration_ms": process_time * 1000}
            )
            raise

        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": process_time * 1000,
            }
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add auth context to requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add auth context to request state."""
        # Extract user info from token if present
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            request.state.token = token

        response = await call_next(request)
        return response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized exception handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and return proper error responses."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"Unhandled exception: {str(exc)}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
