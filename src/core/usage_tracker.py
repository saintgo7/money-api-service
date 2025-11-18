"""Usage tracking and billing."""
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.usage import Usage
from src.models.user import User


class UsageTracker:
    """Track API usage and calculate costs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_usage(
        self,
        user_id: str,
        api_key_id: str,
        endpoint: str,
        method: str,
        tokens: int,
        duration_ms: int,
        status_code: int,
        cost: Decimal,
        metadata: dict = None
    ) -> Usage:
        """Record API usage."""
        if metadata is None:
            metadata = {}

        usage = Usage(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            tokens=tokens,
            duration_ms=duration_ms,
            status_code=status_code,
            cost=cost,
            metadata=metadata
        )

        self.db.add(usage)
        await self.db.commit()

        # Deduct from user credit balance
        await self.deduct_credits(user_id, cost)

        return usage

    async def deduct_credits(self, user_id: str, amount: Decimal):
        """Deduct credits from user balance."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.credit_balance -= amount
            await self.db.commit()

    async def get_usage_stats(
        self,
        user_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> dict:
        """Get usage statistics for a user."""
        query = select(Usage).where(Usage.user_id == user_id)

        if start_date:
            query = query.where(Usage.timestamp >= start_date)
        if end_date:
            query = query.where(Usage.timestamp <= end_date)

        result = await self.db.execute(query)
        usage_records = result.scalars().all()

        total_requests = len(usage_records)
        total_cost = sum(Decimal(str(u.cost)) for u in usage_records)
        total_tokens = sum(u.tokens for u in usage_records)

        # Group by endpoint
        by_endpoint = {}
        for u in usage_records:
            if u.endpoint not in by_endpoint:
                by_endpoint[u.endpoint] = {
                    "requests": 0,
                    "cost": Decimal("0"),
                    "tokens": 0
                }
            by_endpoint[u.endpoint]["requests"] += 1
            by_endpoint[u.endpoint]["cost"] += Decimal(str(u.cost))
            by_endpoint[u.endpoint]["tokens"] += u.tokens

        return {
            "total_requests": total_requests,
            "total_cost": float(total_cost),
            "total_tokens": total_tokens,
            "by_endpoint": {
                k: {
                    "requests": v["requests"],
                    "cost": float(v["cost"]),
                    "tokens": v["tokens"]
                }
                for k, v in by_endpoint.items()
            }
        }

    async def check_credit_balance(self, user_id: str, required_amount: Decimal) -> bool:
        """Check if user has sufficient credits."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        return user.credit_balance >= required_amount
