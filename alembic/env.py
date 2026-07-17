"""
Alembic 环境配置

运行方式:
    alembic revision --autogenerate -m "描述"
    alembic upgrade head
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# 将项目根目录加入 sys.path，确保能导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入应用配置和模型
from app.core.config import settings
from app.db.session import Base

# 导入所有模型，确保 Alembic 能检测到表结构变化
from app.models import (
    User,
    Community,
    Appliance,
    House,
    Contact,
    HouseAppliance,
)

# Alembic Config 对象
config = context.config

# 从 settings 动态设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 设置 target_metadata
# 这样 autogenerate 才能检测到模型变化
target_metadata = Base.metadata

# 解释配置文件中的日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """在离线模式下运行迁移（生成 SQL 脚本，不连接数据库）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在在线模式下运行迁移（连接数据库执行）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 检测字段类型变化
            compare_server_default=True,  # 检测默认值变化
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()