import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.database import get_db, async_session
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "postgresql+asyncpg://wallet_user:wallet_pass@db:5432/wallet_db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def client():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async def override_get_db():
        async_session_test = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session_test() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    await engine.dispose()