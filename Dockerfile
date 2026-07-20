# ============================================================
# AI House Backend - Dockerfile
# 基于 Python 3.12 的 FastAPI 应用
# ============================================================

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（编译 bcrypt、Pillow 等需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令（生产模式，关闭 reload）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
