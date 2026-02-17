"""
User Management Service

A production-grade FastAPI service for managing users and organizations
with JWT authentication, role-based access control, and comprehensive logging.
"""

__version__ = "1.0.0"
__author__ = "Platform Team"
__license__ = "MIT"

from .main import app

__all__ = ["app", "__version__"]
