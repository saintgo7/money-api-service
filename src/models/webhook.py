"""Webhook model."""
from sqlalchemy import Column, String, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.models.base import Base, TimestampMixin


class Webhook(Base, TimestampMixin):
    """Webhook configuration model."""

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Webhook details
    url = Column(String(512), nullable=False)
    secret = Column(String(64), nullable=False)  # For signature verification
    events = Column(JSON, default=[])  # List of events to subscribe to

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    failure_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", backref="webhooks")

    def __repr__(self):
        return f"<Webhook {self.url}>"
