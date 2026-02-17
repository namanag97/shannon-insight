"""
Organization models for request/response validation.

Defines Pydantic models for organization data with validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .permissions import RoleEnum


class OrgCreate(BaseModel):
    """Request model for organization creation."""

    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    description: Optional[str] = Field(
        None, max_length=500, description="Organization description"
    )


class OrgUpdate(BaseModel):
    """Request model for organization updates."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class OrgMemberRole(BaseModel):
    """Request model for organization member role assignment."""

    user_id: int = Field(..., description="User ID")
    role: RoleEnum = Field(..., description="Role in organization")


class OrgMember(BaseModel):
    """Organization member information."""

    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    role: RoleEnum = Field(..., description="Role in organization")
    joined_at: datetime = Field(..., description="Joined timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrgResponse(BaseModel):
    """Response model for organization data."""

    id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    description: Optional[str] = Field(None, description="Organization description")
    owner_id: int = Field(..., description="Owner user ID")
    member_count: int = Field(default=1, description="Number of members")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrgDetailResponse(OrgResponse):
    """Detailed organization response with members."""

    members: list[OrgMember] = Field(default_factory=list, description="Organization members")
