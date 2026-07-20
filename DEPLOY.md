# AI House Backend - Docker 生产部署指南

## 目录

- [方案概述](#方案概述)
- [方案 A：Watchtower 自动更新（推荐）](#方案-a-watchtower-自动更新推荐)
- [方案 B：Webhook 主动推送](#方案-b-webhook-主动推送)
- [首次部署](#首次部署)
- [环境变量配置](#环境变量配置)
- [手动触发更新](#手动触发更新)
- [常见问题](#常见问题)

---

## 方案概述

提供两套自动更新方案，均实现 **Git push → 自动更新 Docker 容器**：

| 方案 | 原理 | 适用场景 | 复杂度 |
|------|------|---------|--------|
| **A. Watchtower** | 定时轮询 Docker Hub，发现新镜像自动拉取重启 | 有 Docker Hub 账号，追求简单 | 低 |
| **B. Webhook** | GitHub Actions 推送后主动通知服务器更新 | 无 Docker Hub 或需要精确控制 | 中 |

---

## 方案 A：Watchtower 自动更新（推荐）

### 1. 注册 Docker Hub 账号

访问 https://hub.docker.com 注册，记住用户名和密码。

### 2. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码（或 Access Token） |

### 3. 配置 GitHub Actions

已配置 `../.github/workflows/docker.yml`，push 到 `main` 分支时自动：
1. 构建后端 Docker 镜像
2. 推送到 Docker Hub（标签：`latest` + `git-sha`）
3. 可选：触发服务器 Webhook 通知

### 4. 服务器首次部署

```bash
# 1. 克隆代码到服务器
git clone https://github.com/yourname/ai-house.git /opt/ai-house
cd /opt/ai-house

# 2. 创建后端环境变量文件
cp backend/.env backend/.env.bak 2>/dev/null || true
cat > backend/.env << 'EOF'
DEBUG=false
DATABASE_URL=mysql+pymysql://root:your-password@mysql:3306/house_management?charset=utf8mb4
JWT_SECRET_KEY=change-this-to-a-random-string-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
AES_SECRET_KEY=0123456789abcdef0123456789abcdef
ALLOWED_ORIGINS=https://your-domain.com
LOGIN_RATE_LIMIT_MAX=10
LOGIN_RATE_LIMIT_WINDOW=300
EOF

# 3. 创建 docker-compose 环境变量文件
cat > .env << 'EOF'
MYSQL_ROOT_PASSWORD=your-strong-password
DOCKER_USERNAME=your-dockerhub-username
WATCHTOWER_TOKEN=your-random-token
EOF

# 4. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 5. 查看后端日志
docker logs -f ai-house-backend
```

### 5. 自动更新流程

```
你 push 代码到 GitHub
       ↓
GitHub Actions 自动构建镜像 → 推送到 Docker Hub
       ↓
Watchtower（每 60 秒轮询）发现 latest 标签有新镜像
       ↓
自动拉取新镜像 → 停止旧容器 → 启动新容器
       ↓
服务更新完成（零人工干预）
```

---

## 方案 B：Webhook 主动推送

如果你不想用 Docker Hub，或需要更精确的更新控制：

### 1. 在服务器部署 Webhook 接收器

```bash
cd /opt/ai-house

# 安装为 systemd 服务
cat > /etc/systemd/system/ai-house-webhook.service << 'EOF'
[Unit]
Description=AI House Webhook Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/ai-house
ExecStart=/usr/bin/python3 server/webhook-server.py
Environment="WEBHOOK_TOKEN=your-secure-token"
Environment="WEBHOOK_PORT=9000"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ai-house-webhook
systemctl start ai-house-webhook
```

### 2. 配置 GitHub Secrets

在仓库 Settings → Secrets 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `WEBHOOK_URL` | `http://你的服务器IP:9000/webhook` |
| `WEBHOOK_TOKEN` | 与服务器上 `WEBHOOK_TOKEN` 一致的 Token |

### 3. 更新流程

```
你 push 代码到 GitHub
       ↓
GitHub Actions 构建镜像 → 推送
       ↓
发送 POST 请求到服务器 Webhook
       ↓
服务器收到通知 → 执行 server/update.sh
       ↓
docker-compose pull → up -d → 更新完成
```

---

## 首次部署

### 准备服务器环境

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
# 重新登录后生效
```

### 目录结构

```
/opt/ai-house/
├── backend/
│   ├── .env              # 后端环境变量（不要提交到 git）
│   ├── Dockerfile        # 后端镜像构建文件
│   ├── DEPLOY.md         # 本文件
│   ├── main.py
│   ├── requirements.txt
│   └── app/
├── admin/
│   └── Dockerfile        # 前端镜像构建文件
├── server/
│   ├── webhook-server.py # Webhook 接收器（方案 B）
│   └── update.sh         # 更新脚本
├── database_init.sql     # 数据库初始化
├── docker-compose.yml    # 开发环境
├── docker-compose.prod.yml  # 生产环境
└── .env                  # docker-compose 变量
```

---

## 环境变量配置

### `backend/.env`（后端配置）

```env
# 生产环境关闭调试
DEBUG=false

# 数据库（docker-compose 会自动覆盖此值）
DATABASE_URL=mysql+pymysql://root:密码@mysql:3306/house_management?charset=utf8mb4

# JWT 密钥（务必修改为随机长字符串）
JWT_SECRET_KEY=change-this-to-a-random-string-at-least-32-chars

# CORS（添加你的前端域名）
ALLOWED_ORIGINS=https://your-domain.com,https://admin.your-domain.com
```

### `.env`（docker-compose 变量，放在项目根目录）

```env
MYSQL_ROOT_PASSWORD=your-strong-mysql-password
DOCKER_USERNAME=your-dockerhub-username
WATCHTOWER_TOKEN=your-random-token
```

---

## 手动触发更新

### 方案 A（Watchtower）

```bash
# 手动触发 Watchtower 立即检查更新
curl -H "Authorization: Bearer your-watchtower-token" \
  http://localhost:8080/v1/update
```

### 方案 B（Webhook）

```bash
# 直接执行更新脚本
bash /opt/ai-house/server/update.sh

# 或发送 Webhook 请求
curl -X POST http://your-server:9000/webhook \
  -H "Authorization: Bearer your-webhook-token" \
  -H "Content-Type: application/json" \
  -d '{"event":"manual"}'
```

---

## 常见问题

### Q1: 数据库数据会丢失吗？

不会。MySQL 数据通过 Docker Volume `mysql_data` 持久化，容器重启不影响数据。

### Q2: 如何查看后端日志？

```bash
docker logs -f ai-house-backend        # 实时日志
docker logs --tail 100 ai-house-backend # 最近 100 行
```

### Q3: 如何重启后端？

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Q4: 更新失败如何回滚？

```bash
# 查看历史镜像
docker images | grep ai-house-backend

# 回滚到指定版本
docker-compose -f docker-compose.prod.yml down
docker tag ai-house-backend:旧版本 ai-house-backend:latest
docker-compose -f docker-compose.prod.yml up -d backend
```

### Q5: 前端（admin/miniprogram）也需要 Docker 化吗？

Admin 是纯前端项目，构建产物是静态文件，推荐：
- 用 `npm run build` 生成 `dist/`
- 用 Nginx 托管静态文件
- 不需要持续运行容器

Miniprogram 是微信小程序，直接上传代码到微信开发者工具即可，无需 Docker。
