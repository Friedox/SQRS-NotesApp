"""add user model

Revision ID: beb2a16e8e61
Revises: 47605fb6295d
Create Date: 2025-05-05 08:41:55.639699

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "beb2a16e8e61"
down_revision: Union[str, None] = "47605fb6295d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user")
