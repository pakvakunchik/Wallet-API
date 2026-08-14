from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import async_engine
from app.models import Base
from app.routers import wallets

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('app started')
    yield
    await async_engine.dispose()
    print('app ended')

app = FastAPI(
    title='Wallet API',
    description='Wallet API',
    version='1.0',
    lifespan=lifespan
)
app.include_router(wallets.router)