import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # e.g.: postgresql+asyncpg://user_name:password@pgdb:5432/database
    "postgresql+asyncpg://app_user:postgres@localhost:5432/app_db",
)

# define async engine with db url
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# session factory that creates async sessions when called:
#   bind: use the async engine
#   class: to create an AsyncSession object
#   expire_on_commit: false, keep their values after commit
#   autoflush: False, flush happens on commit() or when you manually call session.flush().
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    ''' async database session '''
    # Creates an AsyncSession
    async with async_session() as session:
        yield session
