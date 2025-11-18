"""Common API dependencies."""
from typing import Dict
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.api_management import get_api_key_data
from src.core.rate_limiter import rate_limiter


async def verify_and_check_rate_limit(
    request: Request,
    api_key_data: Dict = Depends(get_api_key_data),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Verify API key and check rate limit.

    Returns API key data if successful.
    """
    # Check rate limit
    endpoint = request.url.path
    allowed, info = await rate_limiter.check_rate_limit(
        api_key_data["api_key_id"],
        endpoint,
        api_key_data["rate_limit"]
    )

    # Add rate limit headers info to response (will be added by middleware)
    request.state.rate_limit_info = info

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info["reset_at"])
            }
        )

    return api_key_data
