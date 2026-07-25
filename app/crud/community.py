"""
小区 CRUD
"""
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.community import Community
from app.schemas.community import CommunityCreate, CommunityUpdate


class CRUDCommunity(CRUDBase[Community]):
    def get_by_name(self, db: Session, name: str) -> Community | None:
        return db.query(Community).filter(
            Community.name == name,
            Community.is_deleted == False,  # noqa: E712
        ).first()

    def get_list(
        self,
        db: Session,
        *,
        keyword: str | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> list[Community]:
        query = db.query(Community).filter(
            Community.is_deleted == False,  # noqa: E712
        )
        if keyword:
            query = query.filter(Community.name.contains(keyword))

        # 动态排序
        allowed_sort_fields = {"id", "name", "created_at"}
        if sort_by not in allowed_sort_fields:
            sort_by = "id"
        sort_column = getattr(Community, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session, keyword: str | None = None) -> int:
        from sqlalchemy import func
        query = db.query(func.count(Community.id)).filter(
            Community.is_deleted == False,  # noqa: E712
        )
        if keyword:
            query = query.filter(Community.name.contains(keyword))
        return query.scalar() or 0

    def has_houses(self, db: Session, community_id: int) -> bool:
        from app.models.house import House
        return db.query(House).filter(
            House.community_id == community_id,
            House.is_deleted == False,  # noqa: E712
        ).first() is not None


community_crud = CRUDCommunity(Community)