"""
房源业务逻辑 - 包含状态流转校验
"""
from sqlalchemy import orm
from sqlalchemy.orm import Session

from app.core.security import aes_encrypt, aes_decrypt
from app.crud.house import house_crud
from app.models.house import House
from app.models.contact import Contact
from app.models.house_appliance import HouseAppliance
from app.schemas.house import HouseCreate, HouseUpdate, ApplianceBind

# 合法状态转换规则
VALID_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "空闲": ["在售", "出租中"],
    "在售": ["已售", "空闲", "下架"],
    "出租中": ["已租", "空闲", "下架"],
    "已售": ["空闲"],
    "已租": ["空闲"],
    "下架": ["空闲", "在售", "出租中"],
}

# 合法枚举值
VALID_STATUSES = ["在售", "已售", "空闲", "出租中", "已租", "下架"]
VALID_HOUSE_TYPES = ["住宅", "公寓", "别墅", "商铺"]
VALID_DECORATIONS = ["毛坯", "简装", "精装", "豪装"]
VALID_KEY_TYPES = ["物理钥匙", "密码锁", "无钥匙"]


class HouseService:
    @staticmethod
    def _validate_enums(data: dict) -> None:
        """校验枚举字段合法性"""
        if data.get("status") and data["status"] not in VALID_STATUSES:
            raise ValueError(f"无效的房源状态: {data['status']}")
        if data.get("house_type") and data["house_type"] not in VALID_HOUSE_TYPES:
            raise ValueError(f"无效的房源类型: {data['house_type']}")
        if data.get("decoration") and data["decoration"] not in VALID_DECORATIONS:
            raise ValueError(f"无效的装修状况: {data['decoration']}")
        if data.get("key_type") and data["key_type"] not in VALID_KEY_TYPES:
            raise ValueError(f"无效的钥匙类型: {data['key_type']}")

    @staticmethod
    def _save_contacts(db: Session, house_id: int, contacts_data: list) -> None:
        """保存联系人列表"""
        # 先清除旧联系人
        db.query(Contact).filter(Contact.house_id == house_id).delete()
        # 插入新联系人
        for c in contacts_data:
            contact = Contact(
                house_id=house_id,
                name=c.name,
                phone=c.phone,
                role=c.role,
                is_primary=1 if c.is_primary else 0,
            )
            db.add(contact)

    @staticmethod
    def _save_appliances(db: Session, house_id: int, appliance_binds: list[ApplianceBind] | None) -> None:
        """保存房源-家电关联"""
        # 先清除旧关联
        db.query(HouseAppliance).filter(HouseAppliance.house_id == house_id).delete()
        # 插入新关联
        if appliance_binds:
            for bind in appliance_binds:
                ha = HouseAppliance(
                    house_id=house_id,
                    appliance_id=bind.appliance_id,
                    note=bind.note,
                )
                db.add(ha)

    @staticmethod
    def create_house(db: Session, house_in: HouseCreate) -> House:
        """创建房源（含联系人+家电）"""
        data = house_in.model_dump(exclude={"contacts", "appliance_ids", "lock_password"})

        # 校验枚举
        HouseService._validate_enums(data)

        # 密码锁密码加密
        if house_in.lock_password and house_in.key_type == "密码锁":
            data["lock_password"] = aes_encrypt(house_in.lock_password)
        else:
            data["lock_password"] = None

        # 创建房源
        house = House(**data)
        db.add(house)
        db.flush()

        # 保存联系人
        if house_in.contacts:
            HouseService._save_contacts(db, house.id, house_in.contacts)

        # 保存家电关联
        HouseService._save_appliances(db, house.id, house_in.appliance_ids)

        db.commit()
        db.refresh(house)
        return house

    @staticmethod
    def update_house(db: Session, house: House, house_in: HouseUpdate) -> House:
        """更新房源（含联系人+家电）"""
        data = house_in.model_dump(
            exclude={"contacts", "appliance_ids", "lock_password"},
            exclude_unset=True,
        )

        # 校验枚举
        HouseService._validate_enums(data)

        # 密码锁密码：只有传了才更新
        if house_in.lock_password is not None and (data.get("key_type", house.key_type) == "密码锁" or house_in.key_type == "密码锁"):
            data["lock_password"] = aes_encrypt(house_in.lock_password)

        for field, value in data.items():
            if hasattr(house, field):
                setattr(house, field, value)

        # 更新联系人
        if house_in.contacts is not None:
            HouseService._save_contacts(db, house.id, house_in.contacts)

        # 更新家电关联
        if house_in.appliance_ids is not None:
            HouseService._save_appliances(db, house.id, house_in.appliance_ids)

        db.commit()
        db.refresh(house)
        return house

    @staticmethod
    def update_status(db: Session, house: House, new_status: str) -> House:
        """修改房源状态（含合法性校验）"""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"无效的房源状态: {new_status}")

        allowed = VALID_STATUS_TRANSITIONS.get(house.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"不允许从 '{house.status}' 转换到 '{new_status}'，"
                f"合法目标状态为: {', '.join(allowed) if allowed else '无'}"
            )

        house.status = new_status
        db.commit()
        db.refresh(house)
        return house

    @staticmethod
    def delete_house(db: Session, house: House) -> None:
        """删除房源（级联删除联系人、家电关联）"""
        db.delete(house)
        db.commit()

    @staticmethod
    def get_house_detail(db: Session, house_id: int) -> dict:
        """获取房源详情（含解密密码锁密码、联系人、家电）"""
        house = (
            db.query(House)
            .options(orm.selectinload(House.community))
            .filter(House.id == house_id)
            .first()
        )
        if not house:
            return None

        contacts = (
            db.query(Contact)
            .filter(Contact.house_id == house_id)
            .order_by(Contact.is_primary.desc(), Contact.id.asc())
            .all()
        )

        # 房源-家电关联 + 家电名称
        ha_list = (
            db.query(HouseAppliance)
            .filter(HouseAppliance.house_id == house_id)
            .all()
        )
        appliances = []
        for ha in ha_list:
            # 手动查询家电名称（避免循环导入问题）
            from app.models.appliance import Appliance
            app_obj = db.query(Appliance).filter(Appliance.id == ha.appliance_id).first()
            appliances.append({
                "id": ha.id,
                "appliance_id": ha.appliance_id,
                "appliance_name": app_obj.name if app_obj else None,
                "note": ha.note,
            })

        # 解密密码锁密码
        lock_password = None
        if house.lock_password and house.key_type == "密码锁":
            try:
                lock_password = aes_decrypt(house.lock_password)
            except Exception:
                lock_password = "******（解密失败）"

        return {
            "id": house.id,
            "title": house.title,
            "community_id": house.community_id,
            "community": {
                "id": house.community.id,
                "name": house.community.name,
            } if house.community else None,
            "address": house.address,
            "area": float(house.area) if house.area else None,
            "floor": house.floor,
            "total_floors": house.total_floors,
            "price": float(house.price) if house.price else None,
            "status": house.status,
            "house_type": house.house_type,
            "decoration": house.decoration,
            "key_type": house.key_type,
            "lock_password": lock_password,
            "video_url": house.video_url,
            "images": house.images,
            "description": house.description,
            "contacts": [
                {
                    "id": c.id,
                    "house_id": c.house_id,
                    "name": c.name,
                    "phone": c.phone,
                    "role": c.role,
                    "is_primary": c.is_primary,
                }
                for c in contacts
            ],
            "appliances": appliances,
            "created_at": house.created_at,
            "updated_at": house.updated_at,
        }


house_service = HouseService()