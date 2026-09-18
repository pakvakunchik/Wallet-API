from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.repository.wallet_repository import WalletRepository
from app.schemas import OperationType


class WalletService:
    def __init__(self, repo: WalletRepository):
        self.repo = repo

    async def process_operation(
        self, wallet_id: UUID, op_type: OperationType, amount: Decimal
    ) -> Decimal:
        wallet = await self.repo.get_with_lock(wallet_id)
        if not wallet:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")

        if op_type == OperationType.DEPOSIT:
            wallet.balance += amount
        elif op_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient funds")
            wallet.balance -= amount

        await self.repo.session.flush()
        return wallet.balance

    async def get_balance(self, wallet_id: UUID) -> Decimal:
        balance = await self.repo.get_balance(wallet_id)
        if balance is None:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return balance
