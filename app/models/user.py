"""
用户模型
"""
from datetime import datetime

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="登录账号")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt哈希密码")
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="显示昵称")
    role: Mapped[str] = mapped_column(
        Enum("ADMIN", "USER", name="user_role_enum"),
        nullable=False,
        default="USER",
        comment="角色",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    # houses = relationship("House", back_populates="creator")  # 如果需要记录创建者