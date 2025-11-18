"""Advanced analytics endpoints."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.api_management import verify_api_key
from src.models.usage import Usage

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


@router.get("/usage")
async def get_usage_analytics(
    period: str = Query("7d", regex="^(24h|7d|30d)$"),
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive usage analytics.

    Args:
        period: Time period (24h, 7d, 30d)
        api_key_data: Verified API key data
        db: Database session

    Returns:
        Analytics data with charts and metrics
    """
    user_id = api_key_data["user_id"]

    # Parse period
    period_hours = {
        "24h": 24,
        "7d": 24 * 7,
        "30d": 24 * 30,
    }
    hours = period_hours.get(period, 24 * 7)
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Get usage over time
    from sqlalchemy import select

    # Group by hour for detailed view
    stmt = (
        select(
            func.date_trunc("hour", Usage.timestamp).label("hour"),
            func.count(Usage.id).label("requests"),
            func.sum(Usage.cost).label("cost"),
            func.sum(Usage.tokens).label("tokens"),
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= start_time)
        .group_by("hour")
        .order_by("hour")
    )

    result = await db.execute(stmt)
    usage_over_time = []
    for row in result:
        usage_over_time.append(
            {
                "timestamp": row.hour.isoformat(),
                "requests": row.requests or 0,
                "cost": float(row.cost or 0),
                "tokens": row.tokens or 0,
            }
        )

    # Get endpoint breakdown
    stmt = (
        select(
            Usage.endpoint,
            func.count(Usage.id).label("requests"),
            func.sum(Usage.cost).label("cost"),
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= start_time)
        .group_by(Usage.endpoint)
        .order_by(desc("requests"))
        .limit(10)
    )

    result = await db.execute(stmt)
    total_requests = sum(row.requests for row in result.fetchall())

    result = await db.execute(stmt)
    endpoint_breakdown = []
    for row in result:
        percentage = (row.requests / total_requests * 100) if total_requests > 0 else 0
        endpoint_breakdown.append(
            {
                "endpoint": row.endpoint,
                "requests": row.requests,
                "cost": float(row.cost or 0),
                "percentage": percentage,
            }
        )

    # Get cost breakdown by service type
    stmt = (
        select(
            func.date_trunc("day", Usage.timestamp).label("day"),
            func.sum(
                func.case(
                    (Usage.endpoint.like("%/text/%"), Usage.cost),
                    else_=0,
                )
            ).label("text"),
            func.sum(
                func.case(
                    (Usage.endpoint.like("%/image/%"), Usage.cost),
                    else_=0,
                )
            ).label("image"),
            func.sum(
                func.case(
                    (Usage.endpoint.like("%/audio/%"), Usage.cost),
                    else_=0,
                )
            ).label("audio"),
            func.sum(
                func.case(
                    (Usage.endpoint.like("%/document/%"), Usage.cost),
                    else_=0,
                )
            ).label("document"),
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= start_time)
        .group_by("day")
        .order_by("day")
    )

    result = await db.execute(stmt)
    cost_breakdown = []
    for row in result:
        text = float(row.text or 0)
        image = float(row.image or 0)
        audio = float(row.audio or 0)
        document = float(row.document or 0)
        cost_breakdown.append(
            {
                "category": row.day.strftime("%Y-%m-%d"),
                "text": text,
                "image": image,
                "audio": audio,
                "document": document,
                "total": text + image + audio + document,
            }
        )

    # Get performance metrics
    stmt = (
        select(
            func.date_trunc("hour", Usage.timestamp).label("hour"),
            func.count(Usage.id).label("requests"),
            func.avg(Usage.latency).label("avg_latency"),
            func.percentile_cont(0.95).within_group(Usage.latency).label("p95_latency"),
            func.percentile_cont(0.99).within_group(Usage.latency).label("p99_latency"),
            func.sum(
                func.case(
                    (Usage.status_code >= 400, 1),
                    else_=0,
                )
            ).label("errors"),
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= start_time)
        .group_by("hour")
        .order_by("hour")
    )

    result = await db.execute(stmt)
    performance_metrics = []
    for row in result:
        error_rate = (
            (row.errors / row.requests) if row.requests > 0 else 0
        )
        performance_metrics.append(
            {
                "timestamp": row.hour.isoformat(),
                "requests": row.requests,
                "avg_latency": float(row.avg_latency or 0),
                "p95_latency": float(row.p95_latency or 0),
                "p99_latency": float(row.p99_latency or 0),
                "error_rate": error_rate,
            }
        )

    return {
        "period": period,
        "start_time": start_time.isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "usage_over_time": usage_over_time,
        "endpoint_breakdown": endpoint_breakdown,
        "cost_breakdown": cost_breakdown,
        "performance_metrics": performance_metrics,
    }


@router.get("/summary")
async def get_analytics_summary(
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analytics summary for dashboard.

    Args:
        api_key_data: Verified API key data
        db: Database session

    Returns:
        Summary statistics
    """
    user_id = api_key_data["user_id"]

    # Last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)

    from sqlalchemy import select

    stmt = select(
        func.count(Usage.id).label("total_requests"),
        func.sum(Usage.cost).label("total_cost"),
        func.avg(Usage.latency).label("avg_latency"),
        func.sum(
            func.case(
                (Usage.status_code >= 400, 1),
                else_=0,
            )
        ).label("errors"),
    ).where(
        Usage.user_id == user_id,
        Usage.timestamp >= last_24h,
    )

    result = await db.execute(stmt)
    row = result.first()

    total_requests = row.total_requests or 0
    error_rate = (row.errors / total_requests) if total_requests > 0 else 0

    return {
        "total_requests": total_requests,
        "total_cost": float(row.total_cost or 0),
        "avg_latency": float(row.avg_latency or 0),
        "error_rate": error_rate,
        "period": "24h",
    }
