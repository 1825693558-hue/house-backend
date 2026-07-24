"""add soft delete columns to all tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-24 20:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None

# 所有需要添加软删除字段的表
TABLES = ["users", "communities", "appliances", "houses", "contacts", "house_appliances"]


def upgrade():
    for table in TABLES:
        op.add_column(table, sa.Column(
            "is_deleted", sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
            comment="是否删除",
        ))
        op.add_column(table, sa.Column(
            "deleted_at", sa.DateTime(),
            nullable=True,
            comment="删除时间",
        ))


def downgrade():
    for table in TABLES:
        op.drop_column(table, "deleted_at")
        op.drop_column(table, "is_deleted")
