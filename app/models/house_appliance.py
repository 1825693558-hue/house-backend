"""
房源-家电关联模型
"""
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class HouseAppliance(Base):
    __tablename__ = "house_appliances"
    __table_args__ = (
        UniqueConstraint("house_id", "appliance_id", name="uk_house_appliance"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("houses.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False, index=True, comment="关联房源ID"
    )
    appliance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("appliances.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False, index=True, comment="关联家电类型ID"
    )
    note: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="备注")

    # 关系
    house: Mapped["House"] = relationship(  # noqa: F821
        "House", back_populates="house_appliances"
    )
    appliance: Mapped["Appliance"] = relationship(  # noqa: F821
        "Appliance", back_populates="house_appliances"
    )