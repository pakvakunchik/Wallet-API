"""add server_default and not null for balance

Revision ID: 5263a49349df
Revises: 1e339783ac22
Create Date: 2026-09-18 21:05:51.935868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5263a49349df'
down_revision: Union[str, Sequence[str], None] = '1e339783ac22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "wallets",
        "balance",
        existing_type=sa.Numeric(precision=12, scale=2),
        server_default="0.00",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "wallets",
        "balance",
        existing_type=sa.Numeric(precision=12, scale=2),
        server_default=None,
        existing_nullable=False,
    )
