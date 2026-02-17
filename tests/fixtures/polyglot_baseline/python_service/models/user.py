"""
User models for request/response validation.

Defines Pydantic models for user data with comprehensive validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .permissions import RoleEnum


class UserCreate(BaseModel):
    """Request model for user creation."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Plain text password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    role: RoleEnum = Field(default=RoleEnum.MEMBER, description="User role")


class UserUpdate(BaseModel):
    """Request model for user updates."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    role: RoleEnum = Field(..., description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class UserListResponse(BaseModel):
    """Response model for user list with pagination."""

    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class UserPasswordChange(BaseModel):
    """Request model for password change."""

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
