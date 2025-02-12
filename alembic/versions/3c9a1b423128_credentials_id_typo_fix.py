"""credentials_id typo fix

Revision ID: 3c9a1b423128
Revises: d02e5e065bd5
Create Date: 2025-02-12 19:58:07.685844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '3c9a1b423128'
down_revision: Union[str, None] = 'd02e5e065bd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Get the foreign key constraint name dynamically
    conn = op.get_bind()
    inspector = inspect(conn)

    # Get the foreign keys of the 'passports' table
    foreign_keys = inspector.get_foreign_keys('passports')
    fk_name = None
    for fk in foreign_keys:
        if fk['constrained_columns'] == ['credentials_id']:
            fk_name = fk['name']
            break

    if fk_name:
        # Drop the existing foreign key constraint using the dynamically found name
        with op.batch_alter_table('passports') as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')

    # Rename the column from 'credentials_id' to 'credential_id' (if necessary)
    with op.batch_alter_table('passports') as batch_op:
        batch_op.alter_column('credentials_id', new_column_name='credential_id')

    # Add the new foreign key constraint
    with op.batch_alter_table('passports') as batch_op:
        batch_op.create_foreign_key(
            'fk_passports_credential_id',  # New constraint name
            'visa_center_credentials',  # The referenced table
            ['credentials_id'],  # The new column in the passports table
            ['id'],  # The referenced column in the credentials table
            ondelete='CASCADE'
        )


def downgrade():
    # Get the foreign key constraint name dynamically
    conn = op.get_bind()
    inspector = inspect(conn)

    # Get the foreign keys of the 'passports' table
    foreign_keys = inspector.get_foreign_keys('passports')
    fk_name = None
    for fk in foreign_keys:
        if fk['constrained_columns'] == ['credential_id']:
            fk_name = fk['name']
            break

    if fk_name:
        # Drop the existing foreign key constraint using the dynamically found name
        with op.batch_alter_table('passports') as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')

    # Rename the column back to 'credentials_id'
    with op.batch_alter_table('passports') as batch_op:
        batch_op.alter_column('credential_id', new_column_name='credentials_id')

    # Add the old foreign key constraint back
    with op.batch_alter_table('passports') as batch_op:
        batch_op.create_foreign_key(
            'fk_passports_credentials_id',  # The old constraint name
            'visa_center_credentials',  # The referenced table
            ['credentials_id'],  # The old column name
            ['id'],  # The referenced column in the credentials table
            ondelete='CASCADE'
        )