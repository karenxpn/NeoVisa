"""add country enum change

Revision ID: 5a0bcb2486fb
Revises: 37d919528dbc
Create Date: 2025-01-31 00:30:28.618138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a0bcb2486fb'
down_revision: Union[str, None] = '37d919528dbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Drop the 'visa_center_credentials_new' table if it exists
    op.execute('DROP TABLE IF EXISTS visa_center_credentials_new')

    # Step 2: Create a new table with the correct schema (Enum for the 'country' column)
    op.create_table(
        'visa_center_credentials_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('country', sa.Enum('ES', name='countryenum'), nullable=False, default='ES'),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('encrypted_password', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    )

    # Step 3: Copy data from the old table to the new table
    op.execute(
        'INSERT INTO visa_center_credentials_new (id, country, username, encrypted_password, user_id) '
        'SELECT id, country, username, encrypted_password, user_id FROM visa_center_credentials'
    )

    # Step 4: Drop the old table
    op.drop_table('visa_center_credentials')

    # Step 5: Rename the new table to the original table name
    op.rename_table('visa_center_credentials_new', 'visa_center_credentials')

    # Recreate the indexes if needed
    op.create_index('ix_visa_center_credentials_id', 'visa_center_credentials', ['id'])
    op.create_index('ix_visa_center_credentials_user_id', 'visa_center_credentials', ['user_id'])

def downgrade():
    # Reverse the migration by recreating the old schema
    op.create_table(
        'visa_center_credentials_old',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('country', sa.String(length=5), nullable=True),  # Set to String if downgrading
        sa.Column('username', sa.String, nullable=False),
        sa.Column('encrypted_password', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    )

    # Copy data back from the new table to the old one
    op.execute(
        'INSERT INTO visa_center_credentials_old (id, country, username, encrypted_password, user_id) '
        'SELECT id, country, username, encrypted_password, user_id FROM visa_center_credentials'
    )

    # Drop the current table
    op.drop_table('visa_center_credentials')

    # Rename the old table back to the original table name
    op.rename_table('visa_center_credentials_old', 'visa_center_credentials')

    # Recreate the indexes if needed
    op.create_index('ix_visa_center_credentials_new_id', 'visa_center_credentials', ['id'])
    op.create_index('ix_visa_center_credentials_new_user_id', 'visa_center_credentials', ['user_id'])
