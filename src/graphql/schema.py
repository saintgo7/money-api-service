"""GraphQL schema for Money API Service."""
import strawberry
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


@strawberry.type
class User:
    """User type."""
    id: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    plan: str
    credit_balance: float
    is_active: bool
    created_at: datetime


@strawberry.type
class APIKey:
    """API Key type."""
    id: str
    name: str
    key_prefix: str
    permissions: List[str]
    rate_limit: int
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime


@strawberry.type
class UsageRecord:
    """Usage record type."""
    id: str
    endpoint: str
    method: str
    tokens: int
    duration_ms: int
    cost: float
    timestamp: datetime


@strawberry.type
class UsageStats:
    """Usage statistics type."""
    total_requests: int
    total_cost: float
    total_tokens: int
    by_endpoint: strawberry.scalars.JSON
    period: str


@strawberry.type
class CompletionResult:
    """Text completion result."""
    id: str
    content: str
    model: str
    tokens: int
    cost: float


@strawberry.input
class CompletionInput:
    """Text completion input."""
    prompt: str
    model: str = "claude-sonnet"
    max_tokens: int = 1000
    temperature: float = 0.7


@strawberry.input
class CreateAPIKeyInput:
    """Create API key input."""
    name: str
    permissions: Optional[List[str]] = None


@strawberry.type
class Query:
    """GraphQL queries."""

    @strawberry.field
    async def me(self, info) -> User:
        """Get current user."""
        # This would use the authenticated user from context
        from src.models.user import User as UserModel
        from sqlalchemy import select

        db = info.context["db"]
        user_id = info.context["user_id"]

        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one()

        return User(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            plan=user.plan.value,
            credit_balance=float(user.credit_balance),
            is_active=user.is_active,
            created_at=user.created_at
        )

    @strawberry.field
    async def api_keys(self, info) -> List[APIKey]:
        """List all API keys."""
        from src.models.api_key import APIKey as APIKeyModel
        from sqlalchemy import select

        db = info.context["db"]
        user_id = info.context["user_id"]

        result = await db.execute(
            select(APIKeyModel)
            .where(APIKeyModel.user_id == user_id)
            .order_by(APIKeyModel.created_at.desc())
        )
        keys = result.scalars().all()

        return [
            APIKey(
                id=str(k.id),
                name=k.name,
                key_prefix=k.key_prefix,
                permissions=k.permissions,
                rate_limit=k.rate_limit,
                is_active=k.is_active,
                last_used=k.last_used,
                created_at=k.created_at
            )
            for k in keys
        ]

    @strawberry.field
    async def usage_stats(self, info, period: str = "30d") -> UsageStats:
        """Get usage statistics."""
        from src.core.usage_tracker import UsageTracker
        from datetime import datetime, timedelta

        db = info.context["db"]
        user_id = info.context["user_id"]

        period_map = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }

        start_date = datetime.utcnow() - period_map.get(period, timedelta(days=30))

        tracker = UsageTracker(db)
        stats = await tracker.get_usage_stats(user_id, start_date)

        return UsageStats(
            total_requests=stats["total_requests"],
            total_cost=stats["total_cost"],
            total_tokens=stats["total_tokens"],
            by_endpoint=stats["by_endpoint"],
            period=period
        )

    @strawberry.field
    async def recent_usage(
        self,
        info,
        limit: int = 10
    ) -> List[UsageRecord]:
        """Get recent usage records."""
        from src.models.usage import Usage
        from sqlalchemy import select

        db = info.context["db"]
        user_id = info.context["user_id"]

        result = await db.execute(
            select(Usage)
            .where(Usage.user_id == user_id)
            .order_by(Usage.timestamp.desc())
            .limit(limit)
        )
        records = result.scalars().all()

        return [
            UsageRecord(
                id=str(r.id),
                endpoint=r.endpoint,
                method=r.method,
                tokens=r.tokens,
                duration_ms=r.duration_ms,
                cost=float(r.cost),
                timestamp=r.timestamp
            )
            for r in records
        ]


@strawberry.type
class Mutation:
    """GraphQL mutations."""

    @strawberry.mutation
    async def create_completion(
        self,
        info,
        input: CompletionInput
    ) -> CompletionResult:
        """Generate text completion."""
        import anthropic
        from src.config import get_settings
        from src.core.usage_tracker import UsageTracker
        from decimal import Decimal
        import time

        settings = get_settings()
        db = info.context["db"]
        user_id = info.context["user_id"]
        api_key_id = info.context["api_key_id"]

        # Call Claude
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=input.max_tokens,
            temperature=input.temperature,
            messages=[{"role": "user", "content": input.prompt}]
        )

        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        cost = Decimal(str((tokens / 1000) * settings.price_text_claude))

        # Record usage
        tracker = UsageTracker(db)
        await tracker.record_usage(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint="graphql.createCompletion",
            method="MUTATION",
            tokens=tokens,
            duration_ms=500,
            status_code=200,
            cost=cost
        )

        return CompletionResult(
            id=f"comp_{int(time.time())}",
            content=content,
            model="claude-3-5-sonnet",
            tokens=tokens,
            cost=float(cost)
        )

    @strawberry.mutation
    async def create_api_key(
        self,
        info,
        input: CreateAPIKeyInput
    ) -> APIKey:
        """Create new API key."""
        from src.core.api_management import APIKeyManager

        db = info.context["db"]
        user_id = info.context["user_id"]

        manager = APIKeyManager(db)
        raw_key, api_key = await manager.create_api_key(
            user_id=user_id,
            name=input.name,
            permissions=input.permissions or ["*"],
            rate_limit=60
        )

        return APIKey(
            id=str(api_key.id),
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            permissions=api_key.permissions,
            rate_limit=api_key.rate_limit,
            is_active=api_key.is_active,
            last_used=api_key.last_used,
            created_at=api_key.created_at
        )

    @strawberry.mutation
    async def revoke_api_key(self, info, key_id: str) -> bool:
        """Revoke an API key."""
        from src.core.api_management import APIKeyManager

        db = info.context["db"]
        user_id = info.context["user_id"]

        # Verify ownership
        from src.models.api_key import APIKey as APIKeyModel
        from sqlalchemy import select

        result = await db.execute(
            select(APIKeyModel)
            .where(APIKeyModel.id == key_id)
            .where(APIKeyModel.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise ValueError("API key not found")

        manager = APIKeyManager(db)
        await manager.revoke_api_key(key_id)

        return True


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
