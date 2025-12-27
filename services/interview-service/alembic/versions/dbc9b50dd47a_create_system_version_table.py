"""Create system_version table.

Revision ID: dbc9b50dd47a
Revises: f6de77eb2e44
Create Date: 2025-09-10 13:47:41.087528

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dbc9b50dd47a'
down_revision: str | Sequence[str] | None = '1f2b8ae492b8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'system_version',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
