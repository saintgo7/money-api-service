"""Organization and team models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.models.base import Base


class MemberRole(str, enum.Enum):
    """Team member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Organization(Base):
    """Organization model for team collaboration."""

    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Settings
    billing_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"


class OrganizationMember(Base):
    """Organization member model."""

    __tablename__ = "organization_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization and user
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Role and permissions
    role = Column(SQLEnum(MemberRole), nullable=False, default=MemberRole.DEVELOPER)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="members")

    # Unique constraint: one user per organization
    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
    )

    def __repr__(self):
        return f"<OrganizationMember {self.user_id} in {self.organization_id}>"


# Permission matrix
ROLE_PERMISSIONS = {
    MemberRole.OWNER: {
        "manage_organization": True,
        "manage_members": True,
        "manage_api_keys": True,
        "manage_billing": True,
        "view_usage": True,
        "delete_organization": True,
    },
    MemberRole.ADMIN: {
        "manage_organization": False,
        "manage_members": True,
        "manage_api_keys": True,
        "manage_billing": True,
        "view_usage": True,
        "delete_organization": False,
    },
    MemberRole.DEVELOPER: {
        "manage_organization": False,
        "manage_members": False,
        "manage_api_keys": True,
        "manage_billing": False,
        "view_usage": True,
        "delete_organization": False,
    },
    MemberRole.VIEWER: {
        "manage_organization": False,
        "manage_members": False,
        "manage_api_keys": False,
        "manage_billing": False,
        "view_usage": True,
        "delete_organization": False,
    },
}


def has_permission(role: MemberRole, permission: str) -> bool:
    """Check if a role has a specific permission.

    Args:
        role: Member role
        permission: Permission to check

    Returns:
        True if role has permission, False otherwise
    """
    return ROLE_PERMISSIONS.get(role, {}).get(permission, False)
