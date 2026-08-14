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
        async with self.repo.session.begin():
            wallet = await self.repo.get_with_lock(wallet_id)
            if not wallet:
                raise HTTPException(status_code=404, detail="Wallet not found")
            new_balance = wallet.balance
            if op_type == OperationType.DEPOSIT:
                new_balance += amount
            elif op_type == OperationType.WITHDRAW:
                if wallet.balance < amount:
                    raise HTTPException(status_code=400, detail="Insufficient funds")
                new_balance -= amount
            else:
                raise HTTPException(status_code=400, detail="Invalid operation type")
            await self.repo.update_balance(wallet_id, new_balance)
        return new_balance

    async def get_balance(self, wallet_id: UUID) -> Decimal:
        balance = await self.repo.get_balance(wallet_id)
        if balance is None:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return balance