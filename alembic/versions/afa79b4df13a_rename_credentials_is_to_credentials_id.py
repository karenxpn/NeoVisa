"""rename credentials_is to credentials_id

Revision ID: afa79b4df13a
Revises: 3c9a1b423128
Create Date: 2025-02-12 20:45:00.997115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afa79b4df13a'
down_revision: Union[str, None] = '3c9a1b423128'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('passports', 'credentials_is', new_column_name='credentials_id')


def downgrade() -> None:
    op.alter_column('passports', 'credentials_id', new_column_name='credentials_is')

