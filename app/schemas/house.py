"""
房源相关 Pydantic Schema
"""
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.schemas import fmt_datetime
from app.schemas.contact import ContactCreate, ContactOut
from app.schemas.community import CommunitySimple


# ---------- 联系人/家电嵌套 ----------

class ApplianceBind(BaseModel):
    """绑定家电到房源"""
    appliance_id: int
    note: str | None = None


class ApplianceOut(BaseModel):
    """房源详情中的家电信息"""
    id: int
    appliance_id: int
    appliance_name: str | None = None
    note: str | None = None

    model_config = {"from_attributes": True}


# ---------- 请求 ----------

class HouseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="房源标题")
    community_id: int | None = Field(None, description="关联小区ID")
    address: str | None = Field(None, max_length=200, description="楼号/单元/门牌")
    area: float | None = Field(None, ge=0, description="面积(平方米)")
    floor: int | None = Field(None, ge=0, description="所在楼层")
    total_floors: int | None = Field(None, ge=0, description="总楼层数")
    price: float | None = Field(None, ge=0, description="价格")
    status: str = Field(default="空闲", description="房源状态")
    house_type: str | None = Field(None, description="房源类型")
    decoration: str | None = Field(None, description="装修状况")
    key_type: str = Field(default="无钥匙", description="钥匙类型")
    lock_password: str | None = Field(None, description="密码锁密码(明文，后端加密存储)")
    video_url: str | None = Field(None, max_length=500, description="视频URL")
    images: list[str] | None = Field(None, description="图片URL数组")
    description: str | None = Field(None, description="房源描述")
    contacts: list[ContactCreate] = Field(default_factory=list, description="联系人列表")
    appliance_ids: list[ApplianceBind] | None = Field(None, description="关联家电列表")


class HouseUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    community_id: int | None = Field(None)
    address: str | None = Field(None, max_length=200)
    area: float | None = Field(None, ge=0)
    floor: int | None = Field(None, ge=0)
    total_floors: int | None = Field(None, ge=0)
    price: float | None = Field(None, ge=0)
    house_type: str | None = None
    decoration: str | None = None
    key_type: str | None = None
    lock_password: str | None = Field(None, description="密码锁密码(明文，传了才更新)")
    video_url: str | None = Field(None, max_length=500)
    images: list[str] | None = None
    description: str | None = None
    contacts: list[ContactCreate] | None = None
    appliance_ids: list[ApplianceBind] | None = None


class HouseStatusUpdate(BaseModel):
    status: str = Field(..., description="目标状态")


# ---------- 查询参数 ----------

class HouseQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页条数")
    keyword: str | None = Field(None, description="关键词搜索")
    community_id: int | None = Field(None, description="按小区筛选")
    status: str | None = Field(None, description="按状态筛选(逗号分隔)")
    decoration: str | None = Field(None, description="按装修状况筛选")
    key_type: str | None = Field(None, description="按钥匙类型筛选")
    min_area: float | None = Field(None, ge=0)
    max_area: float | None = Field(None, ge=0)
    min_floor: int | None = Field(None, ge=0)
    max_floor: int | None = Field(None, ge=0)
    start_date: date | None = None
    end_date: date | None = None


# ---------- 响应 ----------

class HouseListOut(BaseModel):
    """列表项（不含联系人/家电详情）"""
    id: int
    title: str
    community_id: int | None
    community_name: str | None = None
    address: str | None
    area: float | None
    floor: int | None
    total_floors: int | None
    price: float | None
    status: str
    house_type: str | None
    decoration: str | None
    key_type: str
    has_lock_password: bool = False
    images: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return fmt_datetime(value)


class HouseDetailOut(BaseModel):
    """房源详情（含联系人、家电）"""
    id: int
    title: str
    community_id: int | None
    community: CommunitySimple | None = None
    address: str | None
    area: float | None
    floor: int | None
    total_floors: int | None
    price: float | None
    status: str
    house_type: str | None
    decoration: str | None
    key_type: str
    lock_password: str | None = Field(None, description="密码锁密码(已解密)")
    video_url: str | None
    images: list[str] | None = None
    description: str | None
    contacts: list[ContactOut] = []
    appliances: list[ApplianceOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return fmt_datetime(value)


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    size: int
    items: list
