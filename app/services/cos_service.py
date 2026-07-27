"""
腾讯云 COS 上传服务
"""
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosException
from app.core.config import settings
from app.schemas.response import ok
import uuid
import os
from datetime import datetime


def _get_client() -> CosS3Client | None:
    """获取 COS 客户端，未配置时返回 None"""
    if not settings.COS_SECRET_ID or not settings.COS_SECRET_KEY or not settings.COS_BUCKET:
        return None
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    return CosS3Client(config)


def _build_key(filename: str) -> str:
    """生成 COS 上的文件 key：house/{yyyyMMdd}/{uuid}.{ext}"""
    ext = os.path.splitext(filename)[1].lower()
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex
    return f"house/{date_str}/{unique_id}{ext}"


def _build_url(key: str) -> str:
    """构造访问 URL"""
    if settings.COS_DOMAIN:
        domain = settings.COS_DOMAIN.rstrip("/")
        return f"{domain}/{key}"
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{key}"


def upload_file(file_obj, filename: str, content_type: str) -> dict:
    """
    上传文件到 COS
    返回: { "url": "...", "key": "...", "size": ... }
    """
    client = _get_client()
    if client is None:
        raise RuntimeError("COS 未配置，请在环境变量中设置 COS_SECRET_ID/COS_SECRET_KEY/COS_BUCKET")

    # 校验文件类型
    allowed_types = [t.strip() for t in settings.COS_ALLOWED_TYPES.split(",") if t.strip()]
    if allowed_types and content_type not in allowed_types:
        raise ValueError(f"不支持的文件类型: {content_type}，允许: {', '.join(allowed_types)}")

    key = _build_key(filename)

    try:
        response = client.put_object(
            Bucket=settings.COS_BUCKET,
            Body=file_obj,
            Key=key,
            ContentType=content_type,
        )
        url = _build_url(key)
        return {"url": url, "key": key, "etag": response.get("ETag", "")}
    except CosException as e:
        raise RuntimeError(f"COS 上传失败: {e}") from e
