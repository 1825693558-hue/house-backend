"""
房源 CRUD - 包含多条件查询
"""
from datetime import date
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.house import House
from app.models.community import Community


class CRUDHouse(CRUDBase[House]):
    def get_with_details(self, db: Session, house_id: int) -> House | None:
        return (
            db.query(House)
            .options(
                joinedload(House.community),
                joinedload(House.contacts),
                joinedload(House.house_appliances).joinedload(
                    # noqa: F821 - lazy import
                    __import__("app.models.house_appliance", fromlist=["HouseAppliance"]).HouseAppliance.appliance
                ) if False else None,  # 使用 selectin 已在 model 中配置
            )
            .filter(House.id == house_id)
            .first()
        )

    def query_houses(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 20,
        keyword: str | None = None,
        community_id: int | None = None,
        status: str | None = None,
        decoration: str | None = None,
        key_type: str | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        min_floor: int | None = None,
        max_floor: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[dict], int]:
        """
        多条件查询房源
        返回: (列表数据, 总数)
        """
        # 基础查询 - 左连接 community 获取名称
        query = (
            db.query(
                House,
                Community.name.label("community_name"),
            )
            .outerjoin(Community, House.community_id == Community.id)
        )
        count_query = db.query(func.count(House.id))

        # 关键词搜索
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    House.title.contains(keyword),
                    Community.name.contains(keyword),
                    House.address.contains(keyword),
                )
            )
            count_query = count_query.filter(
                or_(
                    House.title.contains(keyword),
                    Community.name.contains(keyword),
                    House.address.contains(keyword),
                )
            )

        # 精确筛选
        if community_id is not None:
            query = query.filter(House.community_id == community_id)
            count_query = count_query.filter(House.community_id == community_id)

        # 多值状态筛选
        if status:
            statuses = [s.strip() for s in status.split(",") if s.strip()]
            if statuses:
                query = query.filter(House.status.in_(statuses))
                count_query = count_query.filter(House.status.in_(statuses))

        if decoration:
            query = query.filter(House.decoration == decoration)
            count_query = count_query.filter(House.decoration == decoration)

        if key_type:
            query = query.filter(House.key_type == key_type)
            count_query = count_query.filter(House.key_type == key_type)

        # 范围筛选
        if min_area is not None:
            query = query.filter(House.area >= min_area)
            count_query = count_query.filter(House.area >= min_area)
        if max_area is not None:
            query = query.filter(House.area <= max_area)
            count_query = count_query.filter(House.area <= max_area)

        if min_floor is not None:
            query = query.filter(House.floor >= min_floor)
            count_query = count_query.filter(House.floor >= min_floor)
        if max_floor is not None:
            query = query.filter(House.floor <= max_floor)
            count_query = count_query.filter(House.floor <= max_floor)

        # 时间范围
        if start_date:
            query = query.filter(House.created_at >= start_date)
            count_query = count_query.filter(House.created_at >= start_date)
        if end_date:
            query = query.filter(House.created_at <= end_date)
            count_query = count_query.filter(House.created_at <= end_date)

        # 总数
        total = count_query.scalar() or 0

        # 分页
        offset = (page - 1) * size
        results = query.order_by(House.created_at.desc()).offset(offset).limit(size).all()

        # 组装结果
        items = []
        for house, community_name in results:
            item = {
                "id": house.id,
                "title": house.title,
                "community_id": house.community_id,
                "community_name": community_name,
                "address": house.address,
                "area": float(house.area) if house.area else None,
                "floor": house.floor,
                "total_floors": house.total_floors,
                "price": float(house.price) if house.price else None,
                "status": house.status,
                "house_type": house.house_type,
                "decoration": house.decoration,
                "key_type": house.key_type,
                "has_lock_password": house.lock_password is not None,
                "images": house.images,
                "created_at": house.created_at,
                "updated_at": house.updated_at,
            }
            items.append(item)

        return items, total


house_crud = CRUDHouse(House)