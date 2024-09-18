"""initial migration

Revision ID: 2604d6da3705
Revises: 328d2ff04b08
Create Date: 2024-09-18 17:25:51.620003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2604d6da3705'
down_revision: Union[str, None] = '328d2ff04b08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
