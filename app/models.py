import uuid
from sqlalchemy import UUID, Numeric
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=12,
            scale=2
        ),
        default=Decimal('0.00')
    )

