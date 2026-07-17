"""
Pydantic Schema 共享工具
"""
from datetime import datetime


def fmt_datetime(value: datetime) -> str:
    """统一时间格式化：YYYY-MM-DD HH:mm:ss"""
    if value is None:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")
