"""
小区模型
"""
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="小区名称")
    address: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="小区地址")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )

    # 关系
    houses: Mapped[list["House"]] = relationship(  # noqa: F821
        "House", back_populates="community", lazy="selectin"
    )