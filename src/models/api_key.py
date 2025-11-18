"""API Key model."""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.models.base import Base, TimestampMixin


class APIKey(Base, TimestampMixin):
    """API Key model."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Key details
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    key_prefix = Column(String(16), nullable=False)

    # Permissions
    permissions = Column(ARRAY(String), default=["*"])

    # Rate limiting
    rate_limit = Column(Integer, default=10)  # requests per minute

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="api_keys")

    def __repr__(self):
        return f"<APIKey {self.key_prefix}... ({self.name})>"
