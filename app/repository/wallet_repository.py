from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet


class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_with_lock(self, wallet_id: UUID) -> Wallet | None:
        stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_balance(self, wallet_id: UUID) -> Decimal | None:
        stmt = select(Wallet.balance).where(Wallet.id == wallet_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    async def create(self, wallet: Wallet) -> Wallet:
        self.session.add(wallet)
        await self.session.flush()
        return wallet