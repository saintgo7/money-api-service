"""Webhook notification system."""
import hmac
import hashlib
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.webhook import Webhook

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manage webhook notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    async def send_webhook(
        self,
        webhook: Webhook,
        event: str,
        data: Dict
    ) -> bool:
        """Send webhook notification.

        Args:
            webhook: Webhook configuration
            event: Event name
            data: Event data

        Returns:
            Success status
        """
        payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        import json
        payload_str = json.dumps(payload)
        signature = self.generate_signature(payload_str, webhook.secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_str,
                    headers=headers
                )

                if response.status_code >= 200 and response.status_code < 300:
                    # Reset failure count on success
                    webhook.failure_count = 0
                    await self.db.commit()
                    logger.info(f"Webhook sent successfully: {webhook.url}")
                    return True
                else:
                    logger.warning(
                        f"Webhook failed with status {response.status_code}: {webhook.url}"
                    )
                    webhook.failure_count += 1
                    await self.db.commit()
                    return False

        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            webhook.failure_count += 1
            await self.db.commit()

            # Disable webhook after 10 failures
            if webhook.failure_count >= 10:
                webhook.is_active = False
                await self.db.commit()
                logger.warning(f"Webhook disabled after 10 failures: {webhook.url}")

            return False

    async def notify_event(
        self,
        user_id: str,
        event: str,
        data: Dict
    ):
        """Notify all webhooks for a user about an event.

        Args:
            user_id: User ID
            event: Event name
            data: Event data
        """
        # Get active webhooks for user
        result = await self.db.execute(
            select(Webhook)
            .where(Webhook.user_id == user_id)
            .where(Webhook.is_active == True)
        )
        webhooks = result.scalars().all()

        # Send to webhooks that subscribe to this event
        tasks = []
        for webhook in webhooks:
            if "*" in webhook.events or event in webhook.events:
                tasks.append(self.send_webhook(webhook, event, data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Event names
class WebhookEvents:
    """Webhook event constants."""

    USAGE_THRESHOLD = "usage.threshold_reached"
    CREDIT_LOW = "credit.low"
    CREDIT_DEPLETED = "credit.depleted"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
