"""
房源导出 API - 异步导出（创建任务 / 查询状态 / 下载文件）

解决大数据量导出时前端请求超时的问题：
  1. POST /export  → 创建任务，立即返回 task_id（毫秒级）
  2. GET  /export/{task_id}/status  → 轮询任务进度
  3. GET  /export/{task_id}/download → 任务完成后下载 ZIP 文件
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.dependencies import require_admin
from app.db.session import SessionLocal
from app.schemas.response import ok
from app.services.export_service import create_task, get_task, start_export_task, cleanup_task_file
from app.models.user import User

router = APIRouter()


@router.post("")
def create_export(
    export_type: str = "all",
    keyword: str | None = None,
    status: str | None = None,
    decoration: str | None = None,
    key_type: str | None = None,
    community_id: int | None = None,
    house_use_type: str | None = None,
    current_user: User = Depends(require_admin),
):
    """
    创建导出任务，立即返回 task_id

    - export_type: "all"（全部房源）或 "filtered"（按筛选条件）
    - 其他参数为可选筛选条件，仅在 export_type=filtered 时生效
    """
    filters = {}
    if keyword:
        filters["keyword"] = keyword
    if status:
        filters["status"] = status
    if decoration:
        filters["decoration"] = decoration
    if key_type:
        filters["key_type"] = key_type
    if community_id:
        filters["community_id"] = community_id
    if house_use_type:
        filters["house_use_type"] = house_use_type

    task_id = create_task(export_type, filters if filters else None)

    # 启动后台导出线程
    start_export_task(task_id, SessionLocal)

    return ok(data={"task_id": task_id}, msg="导出任务已创建")


@router.get("/{task_id}/status")
def get_export_status(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """查询导出任务进度"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")

    return ok(data=task.to_dict())


@router.get("/{task_id}/download")
def download_export(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """下载导出的 ZIP 文件"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")

    if task.status == "processing":
        raise HTTPException(status_code=409, detail="任务正在处理中，请稍后再试")

    if task.status == "failed":
        raise HTTPException(status_code=400, detail=f"导出失败: {task.error}")

    if task.status == "pending":
        raise HTTPException(status_code=409, detail="任务排队中，请稍后再试")

    if not task.zip_path or not os.path.exists(task.zip_path):
        raise HTTPException(status_code=404, detail="导出文件不存在，请重新导出")

    return FileResponse(
        path=task.zip_path,
        filename=task.zip_filename or "房源导出.zip",
        media_type="application/zip",
    )


@router.delete("/{task_id}")
def cancel_export(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """取消导出任务并清理文件"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status == "processing":
        raise HTTPException(status_code=409, detail="任务正在处理中，无法取消")

    cleanup_task_file(task_id)
    return ok(msg="任务已清理")
