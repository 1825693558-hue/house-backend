"""
全局统一响应数据结构
所有 API 返回格式：{ code, msg, data }
"""
from typing import Any


def ok(data: Any = None, msg: str = "success") -> dict[str, Any]:
    """成功响应"""
    return {"code": 200, "msg": msg, "data": data}


def fail(code: int = 400, msg: str = "操作失败", data: Any = None) -> dict[str, Any]:
    """失败响应"""
    return {"code": code, "msg": msg, "data": data}
