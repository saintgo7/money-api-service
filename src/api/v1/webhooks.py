"""Webhook management API endpoints."""
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.webhook import Webhook
from src.api.dependencies import verify_and_check_rate_limit

router = APIRouter(prefix="/v1/webhooks", tags=["Webhooks"])


class WebhookCreateRequest(BaseModel):
    """Create webhook request."""
    url: HttpUrl
    events: List[str] = ["*"]


class WebhookResponse(BaseModel):
    """Webhook response."""
    id: str
    url: str
    secret: str  # Only shown on creation
    events: List[str]
    is_active: bool
    failure_count: int


class WebhookListResponse(BaseModel):
    """Webhook list item."""
    id: str
    url: str
    events: List[str]
    is_active: bool
    failure_count: int
    created_at: str


@router.post("", response_model=WebhookResponse)
async def create_webhook(
    request: WebhookCreateRequest,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new webhook.

    Subscribe to events and receive HTTP POST notifications.

    Available events:
    - usage.threshold_reached
    - credit.low
    - credit.depleted
    - api_key.created
    - api_key.revoked
    - subscription.updated
    - payment.succeeded
    - payment.failed
    - * (all events)
    """
    # Generate secret for signature verification
    secret = secrets.token_hex(32)

    webhook = Webhook(
        user_id=api_key_data["user_id"],
        url=str(request.url),
        secret=secret,
        events=request.events,
        is_active=True,
        failure_count=0
    )

    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)

    return WebhookResponse(
        id=str(webhook.id),
        url=webhook.url,
        secret=secret,  # Only shown once
        events=webhook.events,
        is_active=webhook.is_active,
        failure_count=webhook.failure_count
    )


@router.get("", response_model=List[WebhookListResponse])
async def list_webhooks(
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    List all webhooks.

    Returns all webhook configurations for the current user.
    """
    result = await db.execute(
        select(Webhook)
        .where(Webhook.user_id == api_key_data["user_id"])
        .order_by(Webhook.created_at.desc())
    )
    webhooks = result.scalars().all()

    return [
        WebhookListResponse(
            id=str(w.id),
            url=w.url,
            events=w.events,
            is_active=w.is_active,
            failure_count=w.failure_count,
            created_at=w.created_at.isoformat()
        )
        for w in webhooks
    ]


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a webhook.

    Permanently removes the webhook configuration.
    """
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.user_id == api_key_data["user_id"])
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(webhook)
    await db.commit()

    return {"message": "Webhook deleted successfully"}


@router.patch("/{webhook_id}/toggle")
async def toggle_webhook(
    webhook_id: str,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable or disable a webhook.

    Toggles the active status of the webhook.
    """
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.user_id == api_key_data["user_id"])
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook.is_active = not webhook.is_active
    await db.commit()

    return {
        "message": f"Webhook {'enabled' if webhook.is_active else 'disabled'}",
        "is_active": webhook.is_active
    }
