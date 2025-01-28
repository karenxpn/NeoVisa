"""visa center credentials

Revision ID: 9b66999dc910
Revises: 31be58f3cea3
Create Date: 2025-01-28 13:49:59.297822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b66999dc910'
down_revision: Union[str, None] = '31be58f3cea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visa_center_credentials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('encrypted_password', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visa_center_credentials_id'), 'visa_center_credentials', ['id'], unique=False)
    op.create_index(op.f('ix_visa_center_credentials_user_id'), 'visa_center_credentials', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_visa_center_credentials_user_id'), table_name='visa_center_credentials')
    op.drop_index(op.f('ix_visa_center_credentials_id'), table_name='visa_center_credentials')
    op.drop_table('visa_center_credentials')
    # ### end Alembic commands ###
