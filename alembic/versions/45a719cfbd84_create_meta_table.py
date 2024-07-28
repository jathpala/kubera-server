"""Create meta table

Revision ID: 45a719cfbd84
Revises:
Create Date: 2024-07-28 23:53:17.491734

"""
# pylint: disable=missing-function-docstring
# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '45a719cfbd84'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    meta_tbl = op.create_table(
        "meta",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.String, nullable=False)
    )
    op.bulk_insert(
        meta_tbl,
        [
            {"key": "schema", "value": "kubera_server"},
            {"key": "version", "value": "1.0"}
        ]
    )

def downgrade() -> None:
    op.drop_table("meta")
