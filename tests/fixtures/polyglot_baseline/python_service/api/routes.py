"""
FastAPI routes for user and organization management.

Implements REST endpoints for CRUD operations with proper validation,
authentication, and error handling.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..exceptions import AppException, ConflictError, NotFoundError, to_http_exception
from ..models import (
    OrgCreate,
    OrgDetailResponse,
    OrgResponse,
    OrgUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from ..models.permissions import RoleEnum
from ..services import OrgService, UserService
from ..utils import get_logger
from .dependencies import get_current_admin, get_current_user, get_org_service, get_user_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["api"])


# User Routes
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """Create a new user."""
    try:
        user = user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        return user
    except AppException as e:
        raise to_http_exception(e)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: dict = Depends(get_current_user),
):
    """Get user by ID."""
    try:
        user = user_service.get_user_by_id(user_id)
        return {k: v for k, v in user.items() if k != "password_hash"}
    except NotFoundError as e:
        raise to_http_exception(e)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    _: dict = Depends(get_current_admin),
):
    """List all users (admin only)."""
    users, total = user_service.list_users(skip=skip, limit=limit)
    return [
        {k: v for k, v in u.items() if k != "password_hash"}
        for u in users
    ]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user information."""
    # Users can only update themselves unless they're admin
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile"
        )

    try:
        updates = user_data.model_dump(exclude_unset=True)
        user = user_service.update_user(user_id, **updates)
        return user
    except AppException as e:
        raise to_http_exception(e)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: dict = Depends(get_current_admin),
):
    """Delete user (admin only)."""
    try:
        user_service.delete_user(user_id)
    except NotFoundError as e:
        raise to_http_exception(e)


# Organization Routes
@router.post("/organizations", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    org_data: OrgCreate,
    org_service: OrgService = Depends(get_org_service),
    current_user: dict = Depends(get_current_user),
):
    """Create a new organization."""
    try:
        org = org_service.create_org(
            name=org_data.name,
            owner_id=current_user["user_id"],
            description=org_data.description,
        )
        return org
    except AppException as e:
        raise to_http_exception(e)


@router.get("/organizations/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: int,
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """Get organization by ID."""
    try:
        org = org_service.get_org(org_id)
        return org
    except NotFoundError as e:
        raise to_http_exception(e)


@router.get("/organizations", response_model=list[OrgResponse])
async def list_orgs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """List all organizations."""
    orgs, total = org_service.list_orgs(skip=skip, limit=limit)
    return orgs


@router.put("/organizations/{org_id}", response_model=OrgResponse)
async def update_org(
    org_id: int,
    org_data: OrgUpdate,
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """Update organization."""
    try:
        updates = org_data.model_dump(exclude_unset=True)
        org = org_service.update_org(org_id, **updates)
        return org
    except AppException as e:
        raise to_http_exception(e)


@router.delete("/organizations/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    org_id: int,
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """Delete organization."""
    try:
        org_service.delete_org(org_id)
    except NotFoundError as e:
        raise to_http_exception(e)


@router.post("/organizations/{org_id}/members", status_code=status.HTTP_201_CREATED)
async def add_org_member(
    org_id: int,
    user_id: int = Query(..., description="User ID to add"),
    role: RoleEnum = Query(RoleEnum.MEMBER, description="Member role"),
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """Add member to organization."""
    try:
        org_service.add_member(org_id, user_id, role)
        return {"success": True}
    except AppException as e:
        raise to_http_exception(e)


@router.delete("/organizations/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_org_member(
    org_id: int,
    user_id: int,
    org_service: OrgService = Depends(get_org_service),
    _: dict = Depends(get_current_user),
):
    """Remove member from organization."""
    try:
        org_service.remove_member(org_id, user_id)
    except NotFoundError as e:
        raise to_http_exception(e)
