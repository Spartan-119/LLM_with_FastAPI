from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Create async engine
# The 'echo=True' parameter enables SQL query logging, which can be useful for debugging
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create async session
# expire_on_commit=False keeps the detached instance state after commit
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create a base class for declarative class definitions
Base = declarative_base()


async def get_db():
    """
    Dependency function to get a database session.

    This function is typically used with FastAPI's dependency injection system.
    It yields an async session which is automatically closed after the request is completed.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        yield session
