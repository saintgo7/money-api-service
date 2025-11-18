"""Team collaboration endpoints."""
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
import re

from src.core.database import get_db
from src.core.api_management import verify_api_key
from src.models.organization import Organization, OrganizationMember, MemberRole, has_permission
from src.models.user import User

router = APIRouter(prefix="/v1/teams", tags=["Teams"])


# Pydantic models
class CreateOrganizationRequest(BaseModel):
    """Request to create an organization."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255, regex=r"^[a-z0-9-]+$")
    billing_email: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    """Request to update an organization."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    billing_email: Optional[str] = None


class InviteMemberRequest(BaseModel):
    """Request to invite a member."""

    email: str
    role: MemberRole = MemberRole.DEVELOPER


class UpdateMemberRequest(BaseModel):
    """Request to update a member."""

    role: MemberRole


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: str
    name: str
    slug: str
    owner_id: str
    billing_email: Optional[str]
    is_active: bool
    created_at: datetime
    member_count: int


class MemberResponse(BaseModel):
    """Member response."""

    id: str
    user_id: str
    organization_id: str
    role: MemberRole
    is_active: bool
    joined_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None


# Helper functions
async def get_user_from_api_key(api_key_data: Dict, db: AsyncSession) -> User:
    """Get user from API key data."""
    stmt = select(User).where(User.id == api_key_data["user_id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def get_organization_member(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
) -> Optional[OrganizationMember]:
    """Get organization member."""
    stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user_id,
        OrganizationMember.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def check_permission(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    permission: str,
    db: AsyncSession
):
    """Check if user has permission in organization."""
    member = await get_organization_member(org_id, user_id, db)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization"
        )

    if not has_permission(member.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your role ({member.role}) does not have permission: {permission}"
        )

    return member


# Endpoints
@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(
    request: CreateOrganizationRequest,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization.

    The creator becomes the owner.
    """
    user = await get_user_from_api_key(api_key_data, db)

    # Check if slug is available
    stmt = select(Organization).where(Organization.slug == request.slug)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )

    # Create organization
    org = Organization(
        name=request.name,
        slug=request.slug,
        owner_id=user.id,
        billing_email=request.billing_email or user.email,
    )
    db.add(org)
    await db.flush()

    # Add owner as member
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=MemberRole.OWNER,
        invited_by=user.id,
    )
    db.add(member)
    await db.commit()
    await db.refresh(org)

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        owner_id=str(org.owner_id),
        billing_email=org.billing_email,
        is_active=org.is_active,
        created_at=org.created_at,
        member_count=1,
    )


@router.get("/organizations", response_model=List[OrganizationResponse])
async def list_organizations(
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    List all organizations the user is a member of.
    """
    user = await get_user_from_api_key(api_key_data, db)

    # Get all organizations where user is a member
    stmt = (
        select(Organization, func.count(OrganizationMember.id).label("member_count"))
        .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
        .where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True
        )
        .group_by(Organization.id)
    )

    from sqlalchemy import func
    result = await db.execute(stmt)
    orgs = []

    for org, member_count in result:
        orgs.append(
            OrganizationResponse(
                id=str(org.id),
                name=org.name,
                slug=org.slug,
                owner_id=str(org.owner_id),
                billing_email=org.billing_email,
                is_active=org.is_active,
                created_at=org.created_at,
                member_count=member_count,
            )
        )

    return orgs


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization details.
    """
    user = await get_user_from_api_key(api_key_data, db)

    # Verify membership
    member = await get_organization_member(org_id, user.id, db)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Count members
    from sqlalchemy import func
    stmt = select(func.count(OrganizationMember.id)).where(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.is_active == True
    )
    result = await db.execute(stmt)
    member_count = result.scalar()

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        owner_id=str(org.owner_id),
        billing_email=org.billing_email,
        is_active=org.is_active,
        created_at=org.created_at,
        member_count=member_count,
    )


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    request: UpdateOrganizationRequest,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization settings.

    Requires admin or owner role.
    """
    user = await get_user_from_api_key(api_key_data, db)
    await check_permission(org_id, user.id, "manage_organization", db)

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields
    if request.name is not None:
        org.name = request.name
    if request.billing_email is not None:
        org.billing_email = request.billing_email

    await db.commit()
    await db.refresh(org)

    # Count members
    from sqlalchemy import func
    stmt = select(func.count(OrganizationMember.id)).where(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.is_active == True
    )
    result = await db.execute(stmt)
    member_count = result.scalar()

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        owner_id=str(org.owner_id),
        billing_email=org.billing_email,
        is_active=org.is_active,
        created_at=org.created_at,
        member_count=member_count,
    )


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: uuid.UUID,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete organization.

    Only the owner can delete an organization.
    """
    user = await get_user_from_api_key(api_key_data, db)
    await check_permission(org_id, user.id, "delete_organization", db)

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    await db.delete(org)
    await db.commit()

    return {"message": "Organization deleted successfully"}


@router.post("/organizations/{org_id}/members", response_model=MemberResponse)
async def invite_member(
    org_id: uuid.UUID,
    request: InviteMemberRequest,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a member to the organization.

    Requires manage_members permission.
    """
    user = await get_user_from_api_key(api_key_data, db)
    await check_permission(org_id, user.id, "manage_members", db)

    # Find user by email
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    invited_user = result.scalar_one_or_none()

    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email"
        )

    # Check if already a member
    existing_member = await get_organization_member(org_id, invited_user.id, db)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )

    # Create member
    member = OrganizationMember(
        organization_id=org_id,
        user_id=invited_user.id,
        role=request.role,
        invited_by=user.id,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    return MemberResponse(
        id=str(member.id),
        user_id=str(member.user_id),
        organization_id=str(member.organization_id),
        role=member.role,
        is_active=member.is_active,
        joined_at=member.joined_at,
        user_email=invited_user.email,
        user_name=invited_user.name,
    )


@router.get("/organizations/{org_id}/members", response_model=List[MemberResponse])
async def list_members(
    org_id: uuid.UUID,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    List all members of an organization.
    """
    user = await get_user_from_api_key(api_key_data, db)

    # Verify membership
    member = await get_organization_member(org_id, user.id, db)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get all members
    stmt = (
        select(OrganizationMember, User)
        .join(User, OrganizationMember.user_id == User.id)
        .where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.is_active == True
        )
        .order_by(OrganizationMember.joined_at)
    )

    result = await db.execute(stmt)
    members = []

    for member, user_data in result:
        members.append(
            MemberResponse(
                id=str(member.id),
                user_id=str(member.user_id),
                organization_id=str(member.organization_id),
                role=member.role,
                is_active=member.is_active,
                joined_at=member.joined_at,
                user_email=user_data.email,
                user_name=user_data.name,
            )
        )

    return members


@router.patch("/organizations/{org_id}/members/{member_id}", response_model=MemberResponse)
async def update_member(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    request: UpdateMemberRequest,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member's role.

    Requires manage_members permission.
    """
    user = await get_user_from_api_key(api_key_data, db)
    await check_permission(org_id, user.id, "manage_members", db)

    # Get member
    stmt = select(OrganizationMember, User).join(
        User, OrganizationMember.user_id == User.id
    ).where(
        OrganizationMember.id == member_id,
        OrganizationMember.organization_id == org_id
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    member, user_data = row

    # Cannot change owner role
    if member.role == MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner's role"
        )

    member.role = request.role
    await db.commit()
    await db.refresh(member)

    return MemberResponse(
        id=str(member.id),
        user_id=str(member.user_id),
        organization_id=str(member.organization_id),
        role=member.role,
        is_active=member.is_active,
        joined_at=member.joined_at,
        user_email=user_data.email,
        user_name=user_data.name,
    )


@router.delete("/organizations/{org_id}/members/{member_id}")
async def remove_member(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from the organization.

    Requires manage_members permission.
    """
    user = await get_user_from_api_key(api_key_data, db)
    await check_permission(org_id, user.id, "manage_members", db)

    # Get member
    stmt = select(OrganizationMember).where(
        OrganizationMember.id == member_id,
        OrganizationMember.organization_id == org_id
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Cannot remove owner
    if member.role == MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the owner"
        )

    await db.delete(member)
    await db.commit()

    return {"message": "Member removed successfully"}
