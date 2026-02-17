"""
Dependency injection for FastAPI.

Provides database, services, and authentication dependencies.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

from ..config import settings
from ..exceptions import AuthenticationError, to_http_exception
from ..services import AuthService, OrgService, UserService
from ..utils import get_logger

logger = get_logger(__name__)
security = HTTPBearer()

# Global instances (in production, use proper DI framework)
_user_service: Optional[UserService] = None
_org_service: Optional[OrgService] = None
_auth_service: Optional[AuthService] = None


class Database:
    """Database connection wrapper."""

    def __init__(self, url: str = settings.database_url):
        """Initialize database."""
        self.url = url

    def connect(self) -> None:
        """Connect to database."""
        pass

    def disconnect(self) -> None:
        """Disconnect from database."""
        pass


_db: Optional[Database] = None


def get_database() -> Generator[Database, None, None]:
    """Get database dependency."""
    global _db
    if _db is None:
        _db = Database()
        _db.connect()
    try:
        yield _db
    finally:
        pass


def get_user_service(db: Database = Depends(get_database)) -> UserService:
    """Get user service dependency."""
    global _user_service
    if _user_service is None:
        _user_service = UserService(db)
    return _user_service


def get_org_service(
    db: Database = Depends(get_database),
    user_service: UserService = Depends(get_user_service),
) -> OrgService:
    """Get organization service dependency."""
    global _org_service
    if _org_service is None:
        _org_service = OrgService(db, user_service)
    return _org_service


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    """Get authentication service dependency."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService(user_service)
    return _auth_service


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Get current user from JWT token.

    Args:
        credentials: HTTP bearer token from Authorization header
        auth_service: Auth service dependency

    Returns:
        Dictionary with user_id and email

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        user_info = auth_service.verify_token(token)
        return user_info
    except AuthenticationError as e:
        raise to_http_exception(e)


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """
    Get current user and verify admin role.

    Args:
        current_user: Current authenticated user
        user_service: User service dependency

    Returns:
        Current user info

    Raises:
        HTTPException: If user is not admin
    """
    user_id = current_user.get("user_id")
    user = user_service.get_user_by_id(user_id)

    from ..models.permissions import RoleEnum

    if user.get("role") != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )

    return current_user
