"""add sale_price rent_price price_note fields to houses

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-24 21:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('houses', sa.Column(
        'sale_price', sa.Numeric(12, 2),
        nullable=True, comment='出售价格(万元)'
    ))
    op.add_column('houses', sa.Column(
        'rent_price', sa.Numeric(10, 2),
        nullable=True, comment='出租价格(元/月)'
    ))
    op.add_column('houses', sa.Column(
        'price_note', sa.String(200),
        nullable=True, comment='价格备注'
    ))


def downgrade():
    op.drop_column('houses', 'price_note')
    op.drop_column('houses', 'rent_price')
    op.drop_column('houses', 'sale_price')
