"""add media field to houses

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-07-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('houses', sa.Column('media', sa.JSON(), nullable=True, comment='媒体文件数组(图片+视频)'))


def downgrade() -> None:
    op.drop_column('houses', 'media')
