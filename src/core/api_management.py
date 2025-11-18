"""API key management and authentication."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.api_key import APIKey
from src.models.user import User

security = HTTPBearer()


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()


class APIKeyManager:
    """Manage API keys."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: list[str] = None,
        rate_limit: int = 10
    ) -> tuple[str, APIKey]:
        """Create a new API key.

        Returns:
            Tuple of (raw_key, api_key_model)
        """
        if permissions is None:
            permissions = ["*"]

        # Generate key
        raw_key = generate_api_key()
        key_hash = hash_api_key(raw_key)
        key_prefix = raw_key[:8]

        # Create API key record
        api_key = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions,
            rate_limit=rate_limit,
            is_active=True
        )

        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)

        return raw_key, api_key

    async def verify_api_key(self, key: str) -> Optional[Dict]:
        """Verify an API key and return key details.

        Returns:
            Dict with user_id, api_key_id, permissions, rate_limit, plan
        """
        key_hash = hash_api_key(key)

        # Query API key with user
        result = await self.db.execute(
            select(APIKey, User)
            .join(User)
            .where(APIKey.key_hash == key_hash)
            .where(APIKey.is_active == True)
        )
        row = result.first()

        if not row:
            return None

        api_key, user = row

        # Check if expired
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None

        # Update last used
        api_key.last_used = datetime.utcnow()
        await self.db.commit()

        return {
            "user_id": str(user.id),
            "api_key_id": str(api_key.id),
            "permissions": api_key.permissions,
            "rate_limit": api_key.rate_limit,
            "plan": user.plan.value,
            "credit_balance": float(user.credit_balance)
        }

    async def revoke_api_key(self, api_key_id: str):
        """Revoke (deactivate) an API key."""
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == api_key_id)
        )
        api_key = result.scalar_one_or_none()

        if api_key:
            api_key.is_active = False
            await self.db.commit()


async def get_api_key_data(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = None
) -> Dict:
    """Dependency to verify API key from Authorization header.

    Usage in endpoints:
        @router.get("/protected")
        async def protected(api_key_data: Dict = Depends(get_api_key_data)):
            user_id = api_key_data["user_id"]
            ...
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing API key")

    api_key = credentials.credentials
    manager = APIKeyManager(db)
    key_data = await manager.verify_api_key(api_key)

    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")

    return key_data
