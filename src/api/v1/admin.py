"""Admin API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from src.core.database import get_db
from src.models.user import User, PlanType
from src.models.api_key import APIKey
from src.models.usage import Usage

router = APIRouter(prefix="/v1/admin", tags=["Admin"])


# Simple admin authentication (in production, use proper auth)
def verify_admin(admin_key: str = Query(...)):
    """Verify admin access."""
    # In production, use proper authentication
    if admin_key != "admin_secret_key":  # Change this!
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


class UserStats(BaseModel):
    """User statistics."""
    total_users: int
    active_users: int
    by_plan: dict
    new_users_today: int
    new_users_this_month: int


class RevenueStats(BaseModel):
    """Revenue statistics."""
    total_revenue: float
    revenue_today: float
    revenue_this_month: float
    by_plan: dict


class SystemStats(BaseModel):
    """System statistics."""
    total_requests_today: int
    total_requests_this_month: int
    total_cost_today: float
    total_cost_this_month: float
    by_endpoint: dict


@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    _: bool = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics."""
    # Total users
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar()

    # Active users
    active_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_result.scalar()

    # By plan
    by_plan = {}
    for plan in PlanType:
        result = await db.execute(
            select(func.count(User.id)).where(User.plan == plan)
        )
        by_plan[plan.value] = result.scalar()

    # New users today
    today = datetime.utcnow().date()
    today_result = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )
    new_users_today = today_result.scalar()

    # New users this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    month_result = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= month_start
        )
    )
    new_users_this_month = month_result.scalar()

    return UserStats(
        total_users=total_users,
        active_users=active_users,
        by_plan=by_plan,
        new_users_today=new_users_today,
        new_users_this_month=new_users_this_month
    )


@router.get("/stats/revenue", response_model=RevenueStats)
async def get_revenue_stats(
    _: bool = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue statistics."""
    # Total revenue (sum of all usage costs)
    total_result = await db.execute(
        select(func.sum(Usage.cost))
    )
    total_revenue = float(total_result.scalar() or 0)

    # Revenue today
    today = datetime.utcnow().date()
    today_result = await db.execute(
        select(func.sum(Usage.cost)).where(
            func.date(Usage.timestamp) == today
        )
    )
    revenue_today = float(today_result.scalar() or 0)

    # Revenue this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    month_result = await db.execute(
        select(func.sum(Usage.cost)).where(
            Usage.timestamp >= month_start
        )
    )
    revenue_this_month = float(month_result.scalar() or 0)

    # By plan (estimate based on user plan)
    by_plan = {}
    for plan in PlanType:
        result = await db.execute(
            select(func.sum(Usage.cost))
            .join(User, Usage.user_id == User.id)
            .where(User.plan == plan)
            .where(Usage.timestamp >= month_start)
        )
        by_plan[plan.value] = float(result.scalar() or 0)

    return RevenueStats(
        total_revenue=total_revenue,
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        by_plan=by_plan
    )


@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    _: bool = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get system statistics."""
    today = datetime.utcnow().date()
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)

    # Requests today
    today_requests_result = await db.execute(
        select(func.count(Usage.id)).where(
            func.date(Usage.timestamp) == today
        )
    )
    total_requests_today = today_requests_result.scalar()

    # Requests this month
    month_requests_result = await db.execute(
        select(func.count(Usage.id)).where(
            Usage.timestamp >= month_start
        )
    )
    total_requests_this_month = month_requests_result.scalar()

    # Cost today
    today_cost_result = await db.execute(
        select(func.sum(Usage.cost)).where(
            func.date(Usage.timestamp) == today
        )
    )
    total_cost_today = float(today_cost_result.scalar() or 0)

    # Cost this month
    month_cost_result = await db.execute(
        select(func.sum(Usage.cost)).where(
            Usage.timestamp >= month_start
        )
    )
    total_cost_this_month = float(month_cost_result.scalar() or 0)

    # By endpoint (this month)
    by_endpoint = {}
    endpoints_result = await db.execute(
        select(Usage.endpoint, func.count(Usage.id), func.sum(Usage.cost))
        .where(Usage.timestamp >= month_start)
        .group_by(Usage.endpoint)
    )

    for endpoint, count, cost in endpoints_result:
        by_endpoint[endpoint] = {
            "requests": count,
            "cost": float(cost or 0)
        }

    return SystemStats(
        total_requests_today=total_requests_today,
        total_requests_this_month=total_requests_this_month,
        total_cost_today=total_cost_today,
        total_cost_this_month=total_cost_this_month,
        by_endpoint=by_endpoint
    )


@router.get("/users")
async def list_users(
    _: bool = Depends(verify_admin),
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    plan: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all users with pagination."""
    query = select(User).order_by(User.created_at.desc())

    if plan:
        query = query.where(User.plan == PlanType(plan))

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "plan": u.plan.value,
            "credit_balance": float(u.credit_balance),
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]


@router.post("/users/{user_id}/credits")
async def adjust_user_credits(
    user_id: str,
    amount: float,
    _: bool = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """Adjust user credit balance (admin only)."""
    from decimal import Decimal

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.credit_balance += Decimal(str(amount))
    await db.commit()

    return {
        "message": f"Adjusted credits by ${amount}",
        "new_balance": float(user.credit_balance)
    }


@router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: str,
    _: bool = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """Disable user account."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    return {"message": "User disabled successfully"}
