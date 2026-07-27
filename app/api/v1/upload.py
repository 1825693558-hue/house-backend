"""
文件上传 API - 基于腾讯云 COS
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.cos_service import upload_file
from app.schemas.response import ok, fail
from app.api.deps import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()


@router.post("/upload")
async def upload_single_file(
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
):
    """上传单个文件到 COS，返回 URL"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 校验文件大小
    max_size = settings.COS_MAX_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制，最大 {settings.COS_MAX_SIZE_MB}MB")

    try:
        result = upload_file(content, file.filename, file.content_type or "application/octet-stream")
        return ok(result)
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
