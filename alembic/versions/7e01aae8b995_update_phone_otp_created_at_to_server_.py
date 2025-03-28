"""update_phone_otp_created_at_to_server_default

Revision ID: 7e01aae8b995
Revises: da9498858761
Create Date: 2025-03-23 22:08:20.278004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e01aae8b995'
down_revision: Union[str, None] = 'da9498858761'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('phone_otps', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               existing_nullable=True,
               server_default=sa.text('CURRENT_TIMESTAMP'),
               existing_server_default=None)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('phone_otps', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               existing_nullable=True,
               server_default=None,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    # ### end Alembic commands ###
