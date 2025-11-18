"""GraphQL context."""
from typing import Optional
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.api_management import APIKeyManager


async def get_graphql_context(request: Request) -> dict:
    """Get GraphQL context with authentication.

    Args:
        request: FastAPI request

    Returns:
        Context dictionary with db and user info
    """
    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")

    api_key = auth_header.replace("Bearer ", "")

    # Get database session
    db = None
    async for session in get_db():
        db = session
        break

    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    # Verify API key
    manager = APIKeyManager(db)
    key_data = await manager.verify_api_key(api_key)

    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {
        "db": db,
        "user_id": key_data["user_id"],
        "api_key_id": key_data["api_key_id"],
        "rate_limit": key_data["rate_limit"],
        "plan": key_data["plan"]
    }
