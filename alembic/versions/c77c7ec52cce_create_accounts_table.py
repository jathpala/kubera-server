"""Create accounts table

Revision ID: c77c7ec52cce
Revises: 45a719cfbd84
Create Date: 2024-07-29 00:02:30.880395

"""
# pylint: disable=missing-function-docstring
# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c77c7ec52cce'
down_revision: Union[str, None] = '45a719cfbd84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("type", sa.Enum("EQUITY", "ASSET", "LIABILITY", "REVENUE", "EXPENSE", name="type_enum", create_constraint=True), nullable=False)
    )
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.create_check_constraint(
            "name_not_empty",
            sa.sql.func.length("name") > 0
        )


def downgrade() -> None:
    op.drop_table("accounts")
