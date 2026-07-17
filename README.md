# Backend - 房源管理系统 API

房源管理系统的 FastAPI 后端服务，提供统一的 RESTful API。

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| FastAPI | 0.115.6 | 异步 Web 框架 |
| Uvicorn | 0.34.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.36 | ORM |
| Alembic | 1.14.1 | 数据库迁移 |
| PyMySQL | 1.1.1 | MySQL 驱动 |
| PyJWT | 2.10.1 | JWT 认证 |
| bcrypt | 4.2.1 | 密码哈希 |
| cryptography | 44.0.0 | AES 加密 |

## 目录结构

```
backend/
├── alembic/                  # Alembic 数据库迁移
│   ├── versions/             # 迁移版本文件
│   └── env.py                # 迁移环境配置
├── app/
│   ├── api/v1/               # 接口层 (Routers)
│   │   ├── auth.py           # 认证接口
│   │   ├── houses.py         # 房源接口
│   │   ├── communities.py    # 小区接口
│   │   ├── appliances.py     # 家电接口
│   │   └── users.py          # 账号接口
│   ├── core/                 # 核心配置
│   │   ├── config.py         # 环境配置 (pydantic-settings)
│   │   ├── security.py       # bcrypt / JWT / AES 工具
│   │   └── dependencies.py   # get_current_user / require_admin
│   ├── models/               # SQLAlchemy ORM (6张表)
│   ├── schemas/              # Pydantic v2 请求/响应模型
│   ├── services/             # 业务逻辑层
│   │   ├── auth_service.py   # 认证业务
│   │   └── house_service.py  # 房源业务 (含状态流转校验)
│   ├── crud/                 # 数据访问层
│   │   ├── base.py           # 通用 CRUD 基类
│   │   ├── user.py
│   │   ├── house.py          # 多条件查询封装
│   │   ├── community.py
│   │   └── appliance.py
│   └── db/
│       └── session.py        # 数据库连接 / SessionLocal / Base
├── tests/                    # 测试目录
├── alembic.ini               # Alembic 配置文件
├── main.py                   # 应用入口
├── .env                      # 环境变量 (gitignore)
├── .env.example              # 环境变量示例
└── requirements.txt          # 依赖清单
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
# 数据库连接
DATABASE_URL=mysql+pymysql://root:密码@localhost:3306/house_management?charset=utf8mb4

# JWT 密钥
JWT_SECRET_KEY=替换为随机密钥

# AES 加密密钥（必须为 32 字节）
AES_SECRET_KEY=0123456789abcdef0123456789abcdef
```

### 3. 初始化数据库

在项目根目录执行：

```bash
mysql -u root -p < ../database_init.sql
```

脚本会创建数据库、建表，并插入默认管理员账号（`admin` / `admin123`）和 10 种家电类型。

### 4. 启动服务

```bash
python -m uvicorn main:app --reload --port 8000
```

访问 `http://localhost:8000/docs` 查看 Swagger 接口文档。

## 数据库迁移 (Alembic)

```bash
cd backend

# 根据模型变化自动生成迁移脚本
python -m alembic revision --autogenerate -m "描述"

# 执行迁移
python -m alembic upgrade head

# 查看当前版本
python -m alembic current

# 回退一个版本
python -m alembic downgrade -1
```

`alembic.ini` 和 `alembic/env.py` 已配置好，自动读取 `.env` 中的 `DATABASE_URL`。

## 接口概览

所有接口统一响应格式：`{"code": 200, "message": "success", "data": {...}}`

| 模块 | 路径前缀 | 接口数 | 说明 |
|------|----------|--------|------|
| 认证 | `/api/v1/auth` | 2 | 登录、获取当前用户 |
| 房源 | `/api/v1/houses` | 6 | 增删改查、多条件筛选、状态流转 |
| 小区 | `/api/v1/communities` | 4 | 写操作需 ADMIN |
| 家电 | `/api/v1/appliances` | 4 | ADMIN 专属 |
| 账号 | `/api/v1/users` | 4 | ADMIN 专属 |

## 认证方式

JWT Bearer Token，登录接口返回：

```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbG...",
    "token_type": "bearer",
    "user": { "id": 1, "username": "admin", "role": "ADMIN" }
  }
}
```

后续请求在 Header 中携带：

```
Authorization: Bearer eyJhbG...
```

## 安全说明

- **密码存储**：bcrypt 哈希（cost = 12）
- **Token 有效期**：7 天
- **密码锁密码**：AES-256-CBC 加密存储，仅已登录用户可查看明文
- **SQL 注入防护**：全部使用 SQLAlchemy ORM，无原生 SQL 拼接
- **角色权限**：`require_admin` 依赖注入控制 ADMIN 专属接口

## 数据模型

| 表名 | 说明 | 级联规则 |
|------|------|----------|
| `users` | 账号表 | — |
| `communities` | 小区表 | 有房源时禁止删除 |
| `appliances` | 家电类型 | 被引用时禁止删除 |
| `houses` | 房源主表 | 删除时级联删除 contacts + house_appliances |
| `house_appliances` | 房源-家电关联 | — |
| `contacts` | 联系人表 | 删除房源时级联删除 |

### 房源状态流转

```
空闲 → 在售 / 出租中
在售 → 已售 / 空闲 / 下架
出租中 → 已租 / 空闲 / 下架
已售 → 空闲
已租 → 空闲
下架 → 空闲 / 在售 / 出租中
```

非法转换接口会返回 `400` 错误。

## 开发规范

- 新增接口 → 在 `app/api/v1/` 下创建或修改 router 文件
- 新增模型 → 在 `app/models/` 下创建，并在 `app/models/__init__.py` 导出
- 新增 schema → 在 `app/schemas/` 下创建
- 新增 CRUD → 继承 `crud/base.py` 的 `CRUDBase`
- 业务逻辑 → 写入 `app/services/`
