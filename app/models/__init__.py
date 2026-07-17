"""
ORM 模型统一导出
"""
from app.models.user import User
from app.models.community import Community
from app.models.appliance import Appliance
from app.models.house import House
from app.models.contact import Contact
from app.models.house_appliance import HouseAppliance

__all__ = [
    "User",
    "Community",
    "Appliance",
    "House",
    "Contact",
    "HouseAppliance",
]