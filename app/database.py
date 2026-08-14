from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

async_engine = create_async_engine(
    settings.database_url,
    echo=True
)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session