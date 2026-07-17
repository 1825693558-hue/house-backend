"""
应用配置 - 基于环境变量
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置，从 .env 文件和环境变量中读取"""

    # 应用
    PROJECT_NAME: str = "房源管理系统API"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-this"

    # 数据库
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/house_management?charset=utf8mb4"

    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # AES 加密（密码锁密码）
    AES_SECRET_KEY: str = "0123456789abcdef0123456789abcdef"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # 登录限流
    LOGIN_RATE_LIMIT_MAX: int = 10
    LOGIN_RATE_LIMIT_WINDOW: int = 300  # 秒

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()