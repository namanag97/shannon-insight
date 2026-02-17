"""
User business logic service.

Handles user CRUD operations, validation, and business rules.
"""

from typing import Any, Optional

from ..exceptions import ConflictError, NotFoundError, ValidationError
from ..models.permissions import RoleEnum
from ..utils import hash_password
from ..utils.validators import validate_email, validate_username


class UserService:
    """Service for user operations."""

    def __init__(self, db: "Database"):  # noqa: F821
        """Initialize user service with database dependency."""
        self.db = db
        # In-memory store for demonstration (replace with real DB in production)
        self.users: dict[int, dict[str, Any]] = {}
        self.next_id = 1

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: RoleEnum = RoleEnum.MEMBER,
    ) -> dict:
        """
        Create a new user.

        Args:
            email: User email (must be unique)
            username: Username (must be unique)
            password: Plain text password
            full_name: Optional full name
            role: User role

        Returns:
            Created user dictionary

        Raises:
            ValidationError: If validation fails
            ConflictError: If email or username already exists
        """
        email = validate_email(email)
        username = validate_username(username)

        # Check for duplicates
        if any(u["email"] == email for u in self.users.values()):
            raise ConflictError(f"Email already registered: {email}")

        if any(u["username"] == username for u in self.users.values()):
            raise ConflictError(f"Username already taken: {username}")

        user_id = self.next_id
        self.next_id += 1

        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "role": role,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        self.users[user_id] = user
        return {k: v for k, v in user.items() if k != "password_hash"}

    def get_user_by_id(self, user_id: int) -> dict:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User dictionary

        Raises:
            NotFoundError: If user not found
        """
        if user_id not in self.users:
            raise NotFoundError("User", str(user_id))
        return self.users[user_id]

    def get_user_by_email(self, email: str) -> dict:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User dictionary

        Raises:
            NotFoundError: If user not found
        """
        email = validate_email(email)
        for user in self.users.values():
            if user["email"] == email:
                return user
        raise NotFoundError("User", email)

    def list_users(self, skip: int = 0, limit: int = 10) -> tuple[list[dict], int]:
        """
        List all users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum users to return

        Returns:
            Tuple of (user list, total count)
        """
        users_list = list(self.users.values())
        total = len(users_list)
        users_list = users_list[skip : skip + limit]
        return users_list, total

    def update_user(self, user_id: int, **updates: Any) -> dict:
        """
        Update user information.

        Args:
            user_id: User ID
            **updates: Fields to update

        Returns:
            Updated user dictionary

        Raises:
            NotFoundError: If user not found
            ValidationError: If validation fails
        """
        user = self.get_user_by_id(user_id)

        if "email" in updates:
            updates["email"] = validate_email(updates["email"])

        if "username" in updates:
            updates["username"] = validate_username(updates["username"])

        user.update(updates)
        return {k: v for k, v in user.items() if k != "password_hash"}

    def delete_user(self, user_id: int) -> bool:
        """
        Delete user.

        Args:
            user_id: User ID to delete

        Returns:
            True if deleted

        Raises:
            NotFoundError: If user not found
        """
        if user_id not in self.users:
            raise NotFoundError("User", str(user_id))

        del self.users[user_id]
        return True

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """
        Update user password hash.

        Args:
            user_id: User ID
            password_hash: New password hash

        Returns:
            True if updated
        """
        user = self.get_user_by_id(user_id)
        user["password_hash"] = password_hash
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account."""
        user = self.get_user_by_id(user_id)
        user["is_active"] = False
        return True

    def activate_user(self, user_id: int) -> bool:
        """Activate user account."""
        user = self.get_user_by_id(user_id)
        user["is_active"] = True
        return True
