"""
FastAPI application entry point.

Initializes the FastAPI application with middleware, routes, and exception handling.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import router
from .api.middleware import (
    AuthContextMiddleware,
    ExceptionHandlingMiddleware,
    RequestLoggingMiddleware,
)
from .config import settings
from .exceptions import AppException
from .utils import setup_logging


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    setup_logging()

    app = FastAPI(
        title="User Management Service",
        description="Production-grade user and organization management API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters - later middleware wraps earlier ones)
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        """Handle custom application exceptions."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}

    # Include routers
    app.include_router(router)

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
