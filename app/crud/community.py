"""
小区 CRUD
"""
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.community import Community
from app.schemas.community import CommunityCreate, CommunityUpdate


class CRUDCommunity(CRUDBase[Community]):
    def get_by_name(self, db: Session, name: str) -> Community | None:
        return db.query(Community).filter(Community.name == name).first()

    def get_list(
        self,
        db: Session,
        *,
        keyword: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Community]:
        query = db.query(Community)
        if keyword:
            query = query.filter(Community.name.contains(keyword))
        return query.order_by(Community.id.desc()).offset(skip).limit(limit).all()

    def get_count(self, db: Session, keyword: str | None = None) -> int:
        from sqlalchemy import func
        query = db.query(func.count(Community.id))
        if keyword:
            query = query.filter(Community.name.contains(keyword))
        return query.scalar() or 0

    def has_houses(self, db: Session, community_id: int) -> bool:
        from app.models.house import House
        return db.query(House).filter(House.community_id == community_id).first() is not None


community_crud = CRUDCommunity(Community)