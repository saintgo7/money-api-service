"""API management endpoints for developers."""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import get_settings
from src.core.database import get_db
from src.core.api_management import APIKeyManager
from src.core.usage_tracker import UsageTracker
from src.models.user import User, PlanType
from src.models.api_key import APIKey as APIKeyModel
from src.api.dependencies import verify_and_check_rate_limit

settings = get_settings()
router = APIRouter(prefix="/v1/manage", tags=["Management"])


# Request/Response Models
class CreateUserRequest(BaseModel):
    """Create user request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    plan: str
    credit_balance: float
    is_active: bool
    created_at: datetime


class CreateAPIKeyRequest(BaseModel):
    """Create API key request."""
    name: str = Field(..., min_length=1, max_length=255)
    permissions: List[str] = Field(default=["*"])
    rate_limit: Optional[int] = None


class APIKeyResponse(BaseModel):
    """API key response."""
    id: str
    name: str
    key: Optional[str] = None  # Only shown on creation
    key_prefix: str
    permissions: List[str]
    rate_limit: int
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""
    total_requests: int
    total_cost: float
    total_tokens: int
    by_endpoint: dict
    period: str


class AddCreditsRequest(BaseModel):
    """Add credits request."""
    amount: float = Field(..., gt=0, le=10000)


# User Management Endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.

    Register a new developer account with initial free credits.
    """
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        password_hash=pwd_context.hash(request.password),
        full_name=request.full_name,
        company=request.company,
        plan=PlanType.FREE,
        credit_balance=5.00,  # $5 free credits
        is_active=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        plan=user.plan.value,
        credit_balance=float(user.credit_balance),
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information.

    Returns account details including credit balance and plan.
    """
    result = await db.execute(
        select(User).where(User.id == api_key_data["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        plan=user.plan.value,
        credit_balance=float(user.credit_balance),
        is_active=user.is_active,
        created_at=user.created_at
    )


# API Key Management
@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new API key.

    Generate a new API key for accessing the platform.
    Keys can have custom permissions and rate limits.
    """
    # Get user's plan for default rate limit
    result = await db.execute(
        select(User).where(User.id == api_key_data["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Set rate limit based on plan if not specified
    if request.rate_limit is None:
        rate_limits = {
            PlanType.FREE: settings.rate_limit_free,
            PlanType.STARTER: settings.rate_limit_starter,
            PlanType.PRO: settings.rate_limit_pro,
            PlanType.ENTERPRISE: settings.rate_limit_enterprise
        }
        rate_limit = rate_limits.get(user.plan, 10)
    else:
        rate_limit = request.rate_limit

    # Create API key
    manager = APIKeyManager(db)
    raw_key, api_key = await manager.create_api_key(
        user_id=str(user.id),
        name=request.name,
        permissions=request.permissions,
        rate_limit=rate_limit
    )

    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        key=raw_key,  # Only shown once
        key_prefix=api_key.key_prefix,
        permissions=api_key.permissions,
        rate_limit=api_key.rate_limit,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used=api_key.last_used
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    List all API keys for current user.

    Returns all API keys with their status and usage info.
    """
    result = await db.execute(
        select(APIKeyModel)
        .where(APIKeyModel.user_id == api_key_data["user_id"])
        .order_by(APIKeyModel.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=str(key.id),
            name=key.name,
            key=None,  # Never show full key after creation
            key_prefix=key.key_prefix,
            permissions=key.permissions,
            rate_limit=key.rate_limit,
            is_active=key.is_active,
            created_at=key.created_at,
            last_used=key.last_used
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke (deactivate) an API key.

    Permanently disables an API key. Cannot be undone.
    """
    # Verify ownership
    result = await db.execute(
        select(APIKeyModel)
        .where(APIKeyModel.id == key_id)
        .where(APIKeyModel.user_id == api_key_data["user_id"])
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    manager = APIKeyManager(db)
    await manager.revoke_api_key(key_id)

    return {"message": "API key revoked successfully"}


# Usage & Billing
@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    period: str = "30d",
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage statistics.

    View API usage, costs, and request counts for a time period.
    Supports: 24h, 7d, 30d, 90d
    """
    # Parse period
    period_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90)
    }

    if period not in period_map:
        raise HTTPException(status_code=400, detail="Invalid period")

    start_date = datetime.utcnow() - period_map[period]

    # Get usage stats
    tracker = UsageTracker(db)
    stats = await tracker.get_usage_stats(
        user_id=api_key_data["user_id"],
        start_date=start_date
    )

    return UsageStatsResponse(
        total_requests=stats["total_requests"],
        total_cost=stats["total_cost"],
        total_tokens=stats["total_tokens"],
        by_endpoint=stats["by_endpoint"],
        period=period
    )


@router.post("/credits")
async def add_credits(
    request: AddCreditsRequest,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Add credits to account.

    Purchase additional API credits via Stripe or other payment methods.
    Note: In production, this would integrate with payment processor.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == api_key_data["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Add credits (in production, verify payment first)
    from decimal import Decimal
    user.credit_balance += Decimal(str(request.amount))
    await db.commit()

    return {
        "message": "Credits added successfully",
        "new_balance": float(user.credit_balance)
    }


@router.post("/subscription/{plan}")
async def update_subscription(
    plan: str,
    api_key_data: dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Update subscription plan.

    Change to Free, Starter, Pro, or Enterprise plan.
    Note: In production, this would integrate with payment processor.
    """
    # Validate plan
    try:
        plan_type = PlanType(plan.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan type")

    # Get user
    result = await db.execute(
        select(User).where(User.id == api_key_data["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update plan
    old_plan = user.plan
    user.plan = plan_type
    await db.commit()

    # Add plan credits
    plan_credits = {
        PlanType.FREE: 0,
        PlanType.STARTER: 50,
        PlanType.PRO: 200,
        PlanType.ENTERPRISE: 0  # Custom
    }

    if plan_credits[plan_type] > 0:
        from decimal import Decimal
        user.credit_balance += Decimal(str(plan_credits[plan_type]))
        await db.commit()

    return {
        "message": f"Plan updated from {old_plan.value} to {plan_type.value}",
        "new_plan": plan_type.value,
        "credits_added": plan_credits[plan_type],
        "new_balance": float(user.credit_balance)
    }
