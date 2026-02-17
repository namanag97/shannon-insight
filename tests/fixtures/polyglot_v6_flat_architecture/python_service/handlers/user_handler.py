"""User handler - depth 1, imports models directly (no glue layer)."""

from ..models.user import User


def get_user(user_id: int) -> User:
    """Get user by ID - direct model access, no service layer."""
    return User(id=user_id, name="Test User", email="test@example.com")


def create_user(name: str, email: str) -> User:
    """Create user - direct model instantiation."""
    return User(id=1, name=name, email=email)


def list_users() -> list:
    """List all users."""
    return [
        User(id=1, name="Alice", email="alice@example.com"),
        User(id=2, name="Bob", email="bob@example.com"),
    ]
