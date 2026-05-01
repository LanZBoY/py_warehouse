"""add stock_balances and stock_movements

Revision ID: b3a91c5e0d12
Revises: f4bf05f17987
Create Date: 2026-05-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3a91c5e0d12'
down_revision: Union[str, Sequence[str], None] = 'f4bf05f17987'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'stock_balances',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('item_id', sa.UUID(), nullable=False),
        sa.Column('location_id', sa.UUID(), nullable=False),
        sa.Column('quantity', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id']),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'item_id', 'location_id', name='uq_stock_balances_item_location'
        ),
        sa.CheckConstraint('quantity >= 0', name='ck_stock_balances_non_negative'),
    )

    op.create_table(
        'stock_movements',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('item_id', sa.UUID(), nullable=False),
        sa.Column('location_id', sa.UUID(), nullable=False),
        sa.Column(
            'movement_type',
            sa.Enum('INBOUND', 'OUTBOUND', 'ADJUST', name='stockmovementtype'),
            nullable=False,
        ),
        sa.Column('change_qty', sa.BigInteger(), nullable=False),
        sa.Column('quantity_after', sa.BigInteger(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id']),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('change_qty <> 0', name='ck_stock_movements_nonzero'),
    )
    op.create_index(
        'ix_stock_movements_item_loc_time',
        'stock_movements',
        ['item_id', 'location_id', 'created_at'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_stock_movements_item_loc_time', table_name='stock_movements')
    op.drop_table('stock_movements')
    op.drop_table('stock_balances')
    sa.Enum(name='stockmovementtype').drop(op.get_bind())
