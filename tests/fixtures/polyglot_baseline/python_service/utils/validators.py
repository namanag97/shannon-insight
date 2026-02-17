"""
Validation utilities for email, password, and other inputs.

Provides reusable validators for data validation across the service.
"""

import re
from typing import Optional

from ..exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>?")


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        Validated email (lowercase)

    Raises:
        ValidationError: If email is invalid
    """
    email = email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError(f"Invalid email format: {email}")
    return email


def validate_password(password: str, min_length: int = 8, require_special: bool = True) -> str:
    """
    Validate password strength.

    Args:
        password: Password to validate
        min_length: Minimum password length
        require_special: Whether special characters are required

    Returns:
        Validated password

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < min_length:
        raise ValidationError(
            f"Password must be at least {min_length} characters long"
        )

    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one digit")

    if require_special and not any(c in PASSWORD_SPECIAL_CHARS for c in password):
        raise ValidationError(
            "Password must contain at least one special character"
        )

    return password


def validate_username(username: str) -> str:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Validated username

    Raises:
        ValidationError: If username is invalid
    """
    username = username.strip()
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")

    if len(username) > 50:
        raise ValidationError("Username must not exceed 50 characters")

    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise ValidationError(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )

    return username


def validate_org_name(name: str) -> str:
    """Validate organization name."""
    name = name.strip()
    if not name or len(name) > 100:
        raise ValidationError("Organization name must be 1-100 characters")
    return name
