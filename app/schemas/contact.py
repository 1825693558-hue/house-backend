"""
联系人相关 Pydantic Schema
"""
from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="联系人姓名")
    phone: str | None = Field(None, max_length=20, description="联系电话")
    role: str | None = Field(None, max_length=20, description="角色：业主/经纪人/家属")
    is_primary: bool = Field(default=False, description="是否主联系人")


class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, description="联系人姓名")
    phone: str | None = Field(None, max_length=20, description="联系电话")
    role: str | None = Field(None, max_length=20, description="角色：业主/经纪人/家属")
    is_primary: bool | None = Field(None, description="是否主联系人")


class ContactOut(BaseModel):
    id: int
    house_id: int
    name: str
    phone: str | None
    role: str | None
    is_primary: int

    model_config = {"from_attributes": True}