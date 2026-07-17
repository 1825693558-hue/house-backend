"""
家电类型模型
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Appliance(Base):
    __tablename__ = "appliances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="家电名称")
    icon: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="图标URL")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序权重")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )

    # 关系
    house_appliances: Mapped[list["HouseAppliance"]] = relationship(  # noqa: F821
        "HouseAppliance", back_populates="appliance", lazy="selectin"
    )