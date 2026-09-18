import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletBalanceResponse(BaseModel):
    wallet_id: uuid.UUID
    balance: Decimal = Field(description="Текущий баланс кошелька")


class WalletOperationsRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, description="Сумма операций")
