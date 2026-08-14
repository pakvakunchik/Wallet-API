import uuid
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class OperationType(str, Enum):
    DEPOSIT: str = "DEPOSIT"
    WITHDRAW: str = "WITHDRAW"

class WalletBalanceResponse(BaseModel):
    balance: Decimal = Field(description='текущий баланс кошелька')
    model_config = {'from_attributes': True}

class WalletOperationsRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, description='сумма операций')

    @field_validator('amount')
    @classmethod
    def amount_is_positive(cls, val: Decimal):
        if val <= 0:
            raise ValueError('Баланс должен быть положительным')
        return val
    model_config = {'from_attributes': True}