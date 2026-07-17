"""
家电类型 CRUD
"""
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.appliance import Appliance
from app.schemas.appliance import ApplianceCreate, ApplianceUpdate


class CRUDAppliance(CRUDBase[Appliance]):
    def get_list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Appliance]:
        return (
            db.query(Appliance)
            .order_by(Appliance.sort_order.asc(), Appliance.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count(self, db: Session) -> int:
        from sqlalchemy import func
        return db.query(func.count(Appliance.id)).scalar() or 0

    def is_used_by_house(self, db: Session, appliance_id: int) -> bool:
        from app.models.house_appliance import HouseAppliance
        return (
            db.query(HouseAppliance)
            .filter(HouseAppliance.appliance_id == appliance_id)
            .first() is not None
        )


appliance_crud = CRUDAppliance(Appliance)