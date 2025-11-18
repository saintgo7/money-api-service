"""User model."""
from sqlalchemy import Column, String, Boolean, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.models.base import Base, TimestampMixin


class PlanType(str, enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base, TimestampMixin):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company = Column(String(255))

    # Subscription
    plan = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    credit_balance = Column(Numeric(10, 2), default=5.00, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
