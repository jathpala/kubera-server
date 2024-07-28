"""Create transactions table

Revision ID: b7cb7018c715
Revises: c77c7ec52cce
Create Date: 2024-07-29 00:02:41.632798

"""
# pylint: disable=missing-function-docstring
# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b7cb7018c715'
down_revision: Union[str, None] = 'c77c7ec52cce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
