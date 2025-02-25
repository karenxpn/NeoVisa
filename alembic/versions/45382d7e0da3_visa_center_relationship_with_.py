"""visa center relationship with credentials

Revision ID: 45382d7e0da3
Revises: 6718c80d2e70
Create Date: 2025-02-25 18:21:05.203377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '45382d7e0da3'
down_revision: Union[str, None] = '6718c80d2e70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get table inspector to check if the column already exists
    inspector = inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('visa_center_credentials')]

    # Only add the visa_center_id column if it doesn't exist
    if 'visa_center_id' not in columns:
        op.add_column('visa_center_credentials', sa.Column('visa_center_id', sa.Integer(), nullable=False))

    op.create_index(op.f('ix_visa_center_credentials_visa_center_id'), 'visa_center_credentials', ['visa_center_id'], unique=False)
    op.create_foreign_key(None, 'visa_center_credentials', 'visa_centers', ['visa_center_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'visa_center_credentials', type_='foreignkey')
    op.drop_index(op.f('ix_visa_center_credentials_visa_center_id'), table_name='visa_center_credentials')
    op.drop_column('visa_center_credentials', 'visa_center_id')
    # ### end Alembic commands ###
