"""Usage tracking model."""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from src.models.base import Base


class Usage(Base):
    """API usage tracking."""

    __tablename__ = "usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=False, index=True)

    # Request details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)

    # Usage metrics
    tokens = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    status_code = Column(Integer, nullable=False)

    # Cost
    cost = Column(Numeric(10, 6), default=0.0, nullable=False)

    # Additional data
    metadata = Column(JSONB, default={})

    # Composite indexes for analytics
    __table_args__ = (
        Index('ix_usage_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_usage_endpoint_timestamp', 'endpoint', 'timestamp'),
    )

    def __repr__(self):
        return f"<Usage {self.endpoint} at {self.timestamp}>"
