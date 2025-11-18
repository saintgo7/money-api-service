"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.main import app
from src.core.database import get_db
from src.models.base import Base
from src.models.user import User, PlanType
from src.models.api_key import APIKey
from src.core.api_management import generate_api_key, hash_api_key


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/money_api_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    AsyncSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="test@example.com",
        password_hash=pwd_context.hash("testpassword123"),
        full_name="Test User",
        plan=PlanType.PRO,
        credit_balance=100.00,
        is_active=True,
        is_verified=True
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_api_key(db_session: AsyncSession, test_user: User) -> tuple[str, APIKey]:
    """Create test API key."""
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    api_key = APIKey(
        user_id=test_user.id,
        name="Test API Key",
        key_hash=key_hash,
        key_prefix=raw_key[:8],
        permissions=["*"],
        rate_limit=60,
        is_active=True
    )

    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)

    return raw_key, api_key


@pytest.fixture
def auth_headers(test_api_key) -> dict:
    """Create authorization headers."""
    raw_key, _ = test_api_key
    return {"Authorization": f"Bearer {raw_key}"}
