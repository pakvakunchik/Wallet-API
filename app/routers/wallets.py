from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_db
from app.repository.wallet_repository import WalletRepository
from app.schemas import WalletBalanceResponse, WalletOperationsRequest, WalletCreateResponse, WalletCreateRequest
from app.services.wallet_services import WalletService

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


async def get_wallet_service(db: AsyncSession = Depends(get_db)) -> WalletService:
    return WalletService(WalletRepository(db))

@router.post("", response_model=WalletCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
        payload: WalletCreateRequest,
        service: WalletService = Depends(get_wallet_service),
        ) -> WalletCreateResponse:
    wallet = await service.create_wallet(payload.balance)
    return WalletCreateResponse(wallet_id=wallet.id, balance=wallet.balance)


@router.post("/{wallet_uuid}/operation", response_model=WalletBalanceResponse)
async def wallet_operations(
    wallet_uuid: UUID,
    operation: WalletOperationsRequest,
    service: WalletService = Depends(get_wallet_service),
) -> WalletBalanceResponse:
    new_balance = await service.process_operation(
        wallet_uuid, operation.operation_type, operation.amount
    )
    return WalletBalanceResponse(wallet_id=wallet_uuid, balance=new_balance)


@router.get("/{wallet_uuid}", response_model=WalletBalanceResponse)
async def wallet_balance(
    wallet_uuid: UUID,
    service: WalletService = Depends(get_wallet_service),
) -> WalletBalanceResponse:
    balance = await service.get_balance(wallet_uuid)
    return WalletBalanceResponse(wallet_id=wallet_uuid, balance=balance)
