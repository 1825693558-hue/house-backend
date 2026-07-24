"""remove title column from houses

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-25 04:10:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('houses', 'title')


def downgrade():
    op.add_column('houses', sa.Column(
        'title', sa.String(100), nullable=False,
        server_default='', comment='房源标题',
    ))
