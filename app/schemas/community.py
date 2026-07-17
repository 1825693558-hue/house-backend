"""
小区相关 Pydantic Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer

from app.schemas import fmt_datetime


# ---------- 请求 ----------

class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="小区名称")
    address: str | None = Field(None, max_length=200, description="小区地址")


class CommunityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="小区名称")
    address: str | None = Field(None, max_length=200, description="小区地址")


# ---------- 响应 ----------

class CommunityOut(BaseModel):
    id: int
    name: str
    address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return fmt_datetime(value)


class CommunitySimple(BaseModel):
    """下拉选择用"""
    id: int
    name: str

    model_config = {"from_attributes": True}
