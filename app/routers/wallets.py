import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repository.wallet_repository import WalletRepository
from app.services.wallet_services import WalletService
from app.schemas import WalletOperationsRequest, WalletBalanceResponse

router = APIRouter(prefix='/api/v1/wallets', tags=['wallets'])
async def get_wallet_service(db: AsyncSession = Depends(get_db)) -> WalletService:
    repo = WalletRepository(db)
    return WalletService(repo)

@router.post('/{wallet_uuid}/operation')
async def wallet_operations(
    wallet_uuid: uuid.UUID,
    operation: WalletOperationsRequest,
    service: WalletService = Depends(get_wallet_service),
) -> WalletBalanceResponse:
    new_balance = await service.process_operation(
        wallet_uuid,
        operation.operation_type,
        operation.amount
    )
    return WalletBalanceResponse(wallet_id=wallet_uuid, balance=new_balance)

@router.get('/{wallet_uuid}', response_model=WalletBalanceResponse)
async def wallet_balance(
    wallet_uuid: uuid.UUID,
    service: WalletService = Depends(get_wallet_service),
) -> WalletBalanceResponse:
    balance = await service.get_balance(wallet_uuid)
    return WalletBalanceResponse(wallet_id=wallet_uuid, balance=balance)