"""
房源模型 - 核心业务表
"""
from datetime import datetime

from sqlalchemy import (
    String, Integer, Numeric, Text, DateTime, Enum,
    ForeignKey, JSON, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class House(Base):
    __tablename__ = "houses"
    __table_args__ = (
        Index("idx_community_id", "community_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
        Index("idx_floor", "floor"),
        Index("idx_area", "area"),
        Index("idx_decoration", "decoration"),
        Index("idx_key_type", "key_type"),
        Index("idx_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="房源标题")

    # 小区关联
    community_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("communities.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True, comment="关联小区ID"
    )

    # 基本信息
    address: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="楼号/单元/门牌")
    area: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, comment="面积(平方米)")
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="所在楼层")
    total_floors: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="总楼层数")
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True, comment="价格")

    # 状态与类型
    status: Mapped[str] = mapped_column(
        Enum("在售", "已售", "空闲", "出租中", "已租", "下架", name="house_status_enum"),
        nullable=False, comment="房源状态"
    )
    house_type: Mapped[str | None] = mapped_column(
        Enum("住宅", "公寓", "别墅", "商铺", name="house_type_enum"),
        nullable=True, comment="房源类型"
    )
    decoration: Mapped[str | None] = mapped_column(
        Enum("毛坯", "简装", "精装", "豪装", name="decoration_enum"),
        nullable=True, comment="装修状况"
    )

    # 钥匙信息
    key_type: Mapped[str] = mapped_column(
        Enum("物理钥匙", "密码锁", "无钥匙", name="key_type_enum"),
        nullable=False, default="无钥匙", comment="钥匙类型"
    )
    lock_password: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="密码锁密码(AES加密)"
    )

    # 多媒体
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="视频URL")
    images: Mapped[list | None] = mapped_column(JSON, nullable=True, comment="图片URL数组")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="房源描述")

    # 时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    community: Mapped["Community"] = relationship(  # noqa: F821
        "Community", back_populates="houses", lazy="selectin"
    )
    contacts: Mapped[list["Contact"]] = relationship(  # noqa: F821
        "Contact", back_populates="house", lazy="selectin",
        cascade="all, delete-orphan",
    )
    house_appliances: Mapped[list["HouseAppliance"]] = relationship(  # noqa: F821
        "HouseAppliance", back_populates="house", lazy="selectin",
        cascade="all, delete-orphan",
    )