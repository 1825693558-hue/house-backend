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
            .filter(Appliance.is_deleted == False)  # noqa: E712
            .order_by(Appliance.sort_order.asc(), Appliance.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count(self, db: Session) -> int:
        from sqlalchemy import func
        return db.query(func.count(Appliance.id)).filter(
            Appliance.is_deleted == False,  # noqa: E712
        ).scalar() or 0

    def is_used_by_house(self, db: Session, appliance_id: int) -> bool:
        from app.models.house_appliance import HouseAppliance
        from app.models.house import House
        return (
            db.query(HouseAppliance)
            .join(House, HouseAppliance.house_id == House.id)
            .filter(
                HouseAppliance.appliance_id == appliance_id,
                House.is_deleted == False,  # noqa: E712
            )
            .first() is not None
        )


appliance_crud = CRUDAppliance(Appliance)