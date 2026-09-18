from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_engine
from app.routers import wallets


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await async_engine.dispose()


app = FastAPI(
    title="Wallet API",
    description="Сервис управления балансами кошельков",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(wallets.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
