import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from telemetry_api.worker.tasks import device_analytics
from telemetry_api.database.database import get_db
from telemetry_api.database.models import Base
from telemetry_api.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def test_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = test_get_db
device_analytics.AsyncSessionLocal = TestingSessionLocal


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="https://example.com") as client:
        yield client
