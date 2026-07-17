"""
联系人模型
"""
from sqlalchemy import String, Integer, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("houses.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False, index=True, comment="关联房源ID"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="联系人姓名")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="联系电话")
    role: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="角色：业主/经纪人/家属")
    is_primary: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="是否主联系人：1=是，0=否"
    )

    # 关系
    house: Mapped["House"] = relationship(  # noqa: F821
        "House", back_populates="contacts"
    )