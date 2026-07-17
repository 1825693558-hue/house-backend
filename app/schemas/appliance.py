"""
家电类型相关 Pydantic Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field


# ---------- 请求 ----------

class ApplianceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="家电名称")
    icon: str | None = Field(None, max_length=200, description="图标URL")
    sort_order: int = Field(default=0, ge=0, description="排序权重")


class ApplianceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, description="家电名称")
    icon: str | None = Field(None, max_length=200, description="图标URL")
    sort_order: int | None = Field(None, ge=0, description="排序权重")


# ---------- 响应 ----------

class ApplianceOut(BaseModel):
    id: int
    name: str
    icon: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}