from telemetry_api.config import config

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

if config.debug:
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./debug.db"

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True
    )
else:
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{config.postgres_user.get_secret_value()}:{config.postgres_password.get_secret_value()}@{config.postgres_host.get_secret_value()}:{config.postgres_port}/{config.postgres_db}"
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
