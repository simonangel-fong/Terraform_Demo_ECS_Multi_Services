import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # e.g.: postgresql+asyncpg://user_name:password@pgdb:5432/database
    "postgresql+asyncpg://app_user:postgres@localhost:5432/app_db",
)


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


Base = declarative_base()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# Optional: create tables automatically for local/dev when DB_CREATE_ALL=true
async def create_all() -> None:
    from . import models  # noqa: F401 - ensure models are imported
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
