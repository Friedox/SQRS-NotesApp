"""Add notes table

Revision ID: e156db346906
Revises: beb2a16e8e61
Create Date: 2025-05-05 18:27:11.336539

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e156db346906"
down_revision: Union[str, None] = "beb2a16e8e61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "note",
        sa.Column("note_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.user_id"], name=op.f("fk_note_user_id_user")
        ),
        sa.PrimaryKeyConstraint("note_id", name=op.f("pk_note")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("note")
