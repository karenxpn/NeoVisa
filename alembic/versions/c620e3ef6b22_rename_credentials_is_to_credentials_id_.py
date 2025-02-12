"""rename credentials_is to credentials_id and remove credential_id

Revision ID: c620e3ef6b22
Revises: afa79b4df13a
Create Date: 2025-02-12 20:46:21.753006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c620e3ef6b22'
down_revision: Union[str, None] = 'afa79b4df13a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass

