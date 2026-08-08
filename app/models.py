from sqlalchemy import UUID, Numeric
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedColumn


class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'
    id: MappedColumn[UUID] = mapped_column(
        UUID,
        primary_key=True
    )
    balance: MappedColumn[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2
        ),
        default=Decimal('0.00')
    )

