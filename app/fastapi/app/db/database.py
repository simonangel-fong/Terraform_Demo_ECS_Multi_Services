from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config.setting import settings

# define async engine with db url
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,    # enable if debug mode
    pool_pre_ping=True,
    pool_size=20,           # persistent database connections
    max_overflow=40,        # additional temporary connections
    # If PostgreSQL doesn't respond within 10 seconds, the connection attempt fails
    # Disables PostgreSQL's Just-In-Time (JIT) compilation
    connect_args={"timeout": 10, "server_settings": {"jit": "off"}},
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
    ''' 
    Async database session dependency for FastAPI.
    Yields an AsyncSession that automatically closes after use.
    async database session 
    '''
    # Creates an AsyncSession
    async with async_session() as session:
        yield session
