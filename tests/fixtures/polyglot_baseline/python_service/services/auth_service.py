"""
Authentication service.

Handles JWT token creation, validation, and user authentication logic.
"""

from datetime import timedelta
from typing import Optional

from ..exceptions import AuthenticationError, NotFoundError, ValidationError
from ..utils import create_access_token, decode_token, hash_password, verify_password
from ..utils.validators import validate_email, validate_password


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_service: "UserService"):  # noqa: F821
        """Initialize auth service with user service dependency."""
        self.user_service = user_service

    def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dictionary with user_id, email, and token

        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            email = validate_email(email)
        except ValidationError as e:
            raise AuthenticationError(str(e))

        try:
            user = self.user_service.get_user_by_email(email)
        except NotFoundError:
            raise AuthenticationError("Invalid email or password")

        if not user.get("is_active"):
            raise AuthenticationError("User account is disabled")

        if not verify_password(password, user.get("password_hash", "")):
            raise AuthenticationError("Invalid email or password")

        token = self.create_token(user["id"], user["email"])
        return {
            "user_id": user["id"],
            "email": user["email"],
            "access_token": token,
            "token_type": "bearer",
        }

    def create_token(self, user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create access token for user.

        Args:
            user_id: User ID
            email: User email
            expires_delta: Custom expiration time

        Returns:
            JWT access token
        """
        data = {"sub": str(user_id), "email": email}
        return create_access_token(data, expires_delta)

    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Token claims with user_id and email

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        payload = decode_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise AuthenticationError("Invalid token payload")

        return {"user_id": int(user_id), "email": email}

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if successful

        Raises:
            AuthenticationError: If old password is wrong
            ValidationError: If new password is invalid
        """
        try:
            new_password = validate_password(new_password)
        except ValidationError:
            raise

        user = self.user_service.get_user_by_id(user_id)

        if not verify_password(old_password, user.get("password_hash", "")):
            raise AuthenticationError("Current password is incorrect")

        new_hash = hash_password(new_password)
        self.user_service.update_password(user_id, new_hash)
        return True
