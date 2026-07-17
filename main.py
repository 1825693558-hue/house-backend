"""
房源管理系统 - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, houses, communities, appliances, users
from app.core.config import settings
from app.db.session import engine, Base

# 创建数据库表（开发阶段使用，生产环境应通过 Alembic 迁移）
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="房源管理系统 API - 支持房源录入、查询、状态管理等核心功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(houses.router, prefix="/api/v1/houses", tags=["房源"])
app.include_router(communities.router, prefix="/api/v1/communities", tags=["小区"])
app.include_router(appliances.router, prefix="/api/v1/appliances", tags=["家电"])
app.include_router(users.router, prefix="/api/v1/users", tags=["账号"])

@app.get("/", tags=["健康检查"])
async def root():
    return {"status": "ok", "message": "房源管理系统 API 服务运行中"}