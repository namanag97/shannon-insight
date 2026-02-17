"""
Permission and role models.

Defines roles, permissions, and their relationships for access control.
"""

from enum import Enum
from typing import Set

from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class PermissionEnum(str, Enum):
    """Fine-grained permissions."""

    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    AUDIT_READ = "audit:read"


ROLE_PERMISSIONS: dict[RoleEnum, Set[PermissionEnum]] = {
    RoleEnum.ADMIN: {
        PermissionEnum.USER_READ,
        PermissionEnum.USER_CREATE,
        PermissionEnum.USER_UPDATE,
        PermissionEnum.USER_DELETE,
        PermissionEnum.ORG_READ,
        PermissionEnum.ORG_UPDATE,
        PermissionEnum.ORG_DELETE,
        PermissionEnum.AUDIT_READ,
    },
    RoleEnum.MANAGER: {
        PermissionEnum.USER_READ,
        PermissionEnum.USER_CREATE,
        PermissionEnum.USER_UPDATE,
        PermissionEnum.ORG_READ,
        PermissionEnum.AUDIT_READ,
    },
    RoleEnum.MEMBER: {
        PermissionEnum.USER_READ,
        PermissionEnum.ORG_READ,
    },
}


class Permission(BaseModel):
    """Permission model."""

    name: PermissionEnum = Field(..., description="Permission name")
    description: str = Field(..., description="Permission description")

    class Config:
        """Pydantic config."""
        from_attributes = True


class Role(BaseModel):
    """Role model with associated permissions."""

    name: RoleEnum = Field(..., description="Role name")
    permissions: list[PermissionEnum] = Field(
        default_factory=list,
        description="Permissions granted to this role"
    )

    @classmethod
    def from_role_enum(cls, role: RoleEnum) -> "Role":
        """Create Role from RoleEnum with associated permissions."""
        permissions = sorted(ROLE_PERMISSIONS.get(role, set()))
        return cls(name=role, permissions=permissions)

    class Config:
        """Pydantic config."""
        from_attributes = True
