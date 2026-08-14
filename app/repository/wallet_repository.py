from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Wallet

class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_with_lock(self, wallet_id: UUID) -> Wallet | None:
        stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_balance(self, wallet_id: UUID, new_balance: Decimal)-> None:
        stmt = update(Wallet).where(Wallet.id == wallet_id).values(balance=new_balance)
        await self.session.execute(stmt)

    async def get_balance(self, wallet_id: UUID) -> Decimal | None:
        stmt = select(Wallet.balance).where(Wallet.id == wallet_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
