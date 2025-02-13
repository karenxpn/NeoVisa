"""user relationship added to passport

Revision ID: ff0f5ddb9b23
Revises: 2b4bda5a4b63
Create Date: 2025-02-13 17:27:46.911183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff0f5ddb9b23'
down_revision: Union[str, None] = '2b4bda5a4b63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode to apply the changes in SQLite
    with op.batch_alter_table('passports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_index('ix_passports_user_id', ['user_id'])  # Corrected call
        batch_op.create_foreign_key('fk_passports_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')

def downgrade() -> None:
    # Use batch mode to reverse the changes in SQLite
    with op.batch_alter_table('passports', schema=None) as batch_op:
        batch_op.drop_constraint('fk_passports_user_id', type_='foreignkey')  # Corrected call
        batch_op.drop_index('ix_passports_user_id')  # Corrected call
        batch_op.drop_column('user_id')
