"""card type removed, bank name nullable

Revision ID: a77a17863afd
Revises: 5f06fc21b055
Create Date: 2025-02-18 15:58:42.429337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a77a17863afd'
down_revision: Union[str, None] = '5f06fc21b055'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cards', 'bank_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_index('ix_cards_card_type', table_name='cards')
    op.drop_column('cards', 'card_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cards', sa.Column('card_type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_index('ix_cards_card_type', 'cards', ['card_type'], unique=False)
    op.alter_column('cards', 'bank_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
