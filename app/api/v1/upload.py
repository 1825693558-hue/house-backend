"""
文件上传接口
"""
import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.response import ok

router = APIRouter()

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "avi"}

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_file_type(content_type: str, filename: str) -> str:
    """判断文件类型是 image 还是 video"""
    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    if content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in {"jpg", "jpeg", "png", "gif", "webp"}:
        return "image"
    if ext in {"mp4", "mov", "avi"}:
        return "video"
    return "image"  # 默认当图片


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
):
    """上传文件（图片/视频）"""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: {ext}，支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_type = _get_file_type(file.content_type or "", file.filename)
    filename = f"{uuid.uuid4().hex}.{ext}"
    _ensure_upload_dir()
    save_path = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    # 限制文件大小：图片 10MB，视频 100MB
    max_size = 10 * 1024 * 1024 if file_type == "image" else 100 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{'图片' if file_type == 'image' else '视频'}文件不能超过{'10MB' if file_type == 'image' else '100MB'}",
        )

    with open(save_path, "wb") as f:
        f.write(content)

    return ok(data={"url": f"/uploads/{filename}", "type": file_type}, msg="上传成功")
