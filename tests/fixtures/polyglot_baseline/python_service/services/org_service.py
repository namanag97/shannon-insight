"""
Organization business logic service.

Handles organization CRUD operations, member management, and business rules.
"""

from typing import Any, Optional

from ..exceptions import ConflictError, NotFoundError, ValidationError
from ..models.permissions import RoleEnum
from ..utils.validators import validate_org_name


class OrgService:
    """Service for organization operations."""

    def __init__(self, db: "Database", user_service: "UserService"):  # noqa: F821
        """Initialize org service with dependencies."""
        self.db = db
        self.user_service = user_service
        # In-memory store for demonstration
        self.orgs: dict[int, dict[str, Any]] = {}
        self.org_members: dict[int, dict[int, RoleEnum]] = {}
        self.next_id = 1

    def create_org(self, name: str, owner_id: int, description: Optional[str] = None) -> dict:
        """
        Create a new organization.

        Args:
            name: Organization name
            owner_id: Owner user ID
            description: Optional description

        Returns:
            Created organization

        Raises:
            ValidationError: If validation fails
            NotFoundError: If owner not found
        """
        name = validate_org_name(name)
        self.user_service.get_user_by_id(owner_id)  # Verify owner exists

        org_id = self.next_id
        self.next_id += 1

        org = {
            "id": org_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "member_count": 1,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        self.orgs[org_id] = org
        self.org_members[org_id] = {owner_id: RoleEnum.ADMIN}
        return org

    def get_org(self, org_id: int) -> dict:
        """
        Get organization by ID.

        Args:
            org_id: Organization ID

        Returns:
            Organization dictionary

        Raises:
            NotFoundError: If org not found
        """
        if org_id not in self.orgs:
            raise NotFoundError("Organization", str(org_id))
        return self.orgs[org_id]

    def list_orgs(self, skip: int = 0, limit: int = 10) -> tuple[list[dict], int]:
        """List all organizations with pagination."""
        orgs_list = list(self.orgs.values())
        total = len(orgs_list)
        orgs_list = orgs_list[skip : skip + limit]
        return orgs_list, total

    def update_org(self, org_id: int, **updates: Any) -> dict:
        """
        Update organization.

        Args:
            org_id: Organization ID
            **updates: Fields to update

        Returns:
            Updated organization

        Raises:
            NotFoundError: If org not found
        """
        org = self.get_org(org_id)

        if "name" in updates:
            updates["name"] = validate_org_name(updates["name"])

        org.update(updates)
        return org

    def delete_org(self, org_id: int) -> bool:
        """
        Delete organization.

        Args:
            org_id: Organization ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If org not found
        """
        if org_id not in self.orgs:
            raise NotFoundError("Organization", str(org_id))

        del self.orgs[org_id]
        if org_id in self.org_members:
            del self.org_members[org_id]
        return True

    def add_member(self, org_id: int, user_id: int, role: RoleEnum = RoleEnum.MEMBER) -> bool:
        """
        Add member to organization.

        Args:
            org_id: Organization ID
            user_id: User ID to add
            role: Member role

        Returns:
            True if added

        Raises:
            NotFoundError: If org or user not found
            ConflictError: If user already a member
        """
        org = self.get_org(org_id)
        self.user_service.get_user_by_id(user_id)  # Verify user exists

        if org_id not in self.org_members:
            self.org_members[org_id] = {}

        if user_id in self.org_members[org_id]:
            raise ConflictError(f"User {user_id} is already a member of org {org_id}")

        self.org_members[org_id][user_id] = role
        org["member_count"] = len(self.org_members[org_id])
        return True

    def remove_member(self, org_id: int, user_id: int) -> bool:
        """
        Remove member from organization.

        Args:
            org_id: Organization ID
            user_id: User ID to remove

        Returns:
            True if removed

        Raises:
            NotFoundError: If org not found or user not a member
        """
        org = self.get_org(org_id)

        if org_id not in self.org_members or user_id not in self.org_members[org_id]:
            raise NotFoundError("Organization member", f"{org_id}/{user_id}")

        del self.org_members[org_id][user_id]
        org["member_count"] = len(self.org_members[org_id])
        return True

    def update_member_role(self, org_id: int, user_id: int, role: RoleEnum) -> bool:
        """
        Update member role in organization.

        Args:
            org_id: Organization ID
            user_id: User ID
            role: New role

        Returns:
            True if updated
        """
        org = self.get_org(org_id)

        if org_id not in self.org_members or user_id not in self.org_members[org_id]:
            raise NotFoundError("Organization member", f"{org_id}/{user_id}")

        self.org_members[org_id][user_id] = role
        return True

    def get_members(self, org_id: int) -> dict[int, RoleEnum]:
        """Get all members of an organization."""
        org = self.get_org(org_id)
        return self.org_members.get(org_id, {})
