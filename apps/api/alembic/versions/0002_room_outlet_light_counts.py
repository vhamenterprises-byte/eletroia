"""add outlet_count and light_point_count to rooms

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("outlet_count", sa.Integer(), nullable=True))
    op.add_column("rooms", sa.Column("light_point_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("rooms", "light_point_count")
    op.drop_column("rooms", "outlet_count")
