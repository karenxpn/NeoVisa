"""add country enum to visa_center_credentials

Revision ID: 37d919528dbc
Revises: 6b784d19ad65
Create Date: 2025-01-31 00:22:11.682790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37d919528dbc'
down_revision: Union[str, None] = '6b784d19ad65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create a new table with the correct schema (country NOT NULL, default value)
    op.create_table(
        'visa_center_credentials_new',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('country', sa.String(length=5), nullable=False, server_default='ES'),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('encrypted_password', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
    )

    # Copy data from the old table to the new table
    op.execute(
        'INSERT INTO visa_center_credentials_new (id, country, username, encrypted_password, user_id) '
        'SELECT id, country, username, encrypted_password, user_id FROM visa_center_credentials'
    )

    # Drop the old table
    op.drop_table('visa_center_credentials')

    # Rename the new table to the original table name
    op.rename_table('visa_center_credentials_new', 'visa_center_credentials')

def downgrade():
    # Recreate the original table with nullable country column
    op.create_table(
        'visa_center_credentials_old',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('country', sa.String(length=5), nullable=True),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('encrypted_password', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
    )

    # Copy data back from the current table to the old table
    op.execute(
        'INSERT INTO visa_center_credentials_old (id, country, username, encrypted_password, user_id) '
        'SELECT id, country, username, encrypted_password, user_id FROM visa_center_credentials'
    )

    # Drop the current table
    op.drop_table('visa_center_credentials')

    # Rename the old table back to the original table name
    op.rename_table('visa_center_credentials_old', 'visa_center_credentials')