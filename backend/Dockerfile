# Stage 1: Build stage
FROM python:3.12-slim

# 设置环境变量以禁用缓冲模式
ENV PYTHONUNBUFFERED=1

# 安装系统依赖项
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    build-essential \
    gcc \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*


# 设置工作目录
WORKDIR /app

# 升级 pip
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . /app/

# 确保 init.sh 可执行
COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# 创建非 root 用户
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app && \
    chown -R appuser:appuser /app/staticfiles

# 切换到非 root 用户
USER appuser

# 启动脚本
CMD ["/app/init.sh"]