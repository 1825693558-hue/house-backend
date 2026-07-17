"""
用户相关 Pydantic Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer

from app.schemas import fmt_datetime


# ---------- 请求 ----------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="登录账号")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str | None = Field(None, max_length=50, description="显示昵称")
    role: str = Field(default="USER", pattern=r"^(ADMIN|USER)$", description="角色")


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="显示昵称")
    role: str | None = Field(None, pattern=r"^(ADMIN|USER)$", description="角色")
    password: str | None = Field(None, min_length=6, max_length=100, description="新密码（不传则不修改）")


# ---------- 响应 ----------

class UserOut(BaseModel):
    id: int
    username: str
    nickname: str | None
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return fmt_datetime(value)
