#!/bin/bash

# 打印环境变量用于调试
echo "Environment variables:"
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_USER: $DB_USER"
echo "REDIS_HOST: $REDIS_HOST"
echo "REDIS_PORT: $REDIS_PORT"

# 设置最大等待时间（秒）
MAX_WAIT=60
start_time=$(date +%s)

# 等待数据库准备就绪
echo "Waiting for database to be ready..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2> /dev/null; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    
    if [ $elapsed_time -gt $MAX_WAIT ]; then
        echo "Timeout waiting for database"
        exit 1
    fi
    
    echo "Waiting for database... (${elapsed_time}s)"
    sleep 2
done

echo "Database is ready."

# 等待Redis准备就绪
start_time=$(date +%s)
echo "Waiting for Redis to be ready..."
until redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2> /dev/null; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    
    if [ $elapsed_time -gt $MAX_WAIT ]; then
        echo "Timeout waiting for Redis"
        exit 1
    fi
    
    echo "Waiting for Redis... (${elapsed_time}s)"
    sleep 2
done

echo "Redis is ready."

# 运行Django迁移
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# 创建超级用户（如果不存在）
echo "Creating superuser if it doesn't exist..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', os.environ.get('ADMIN_PASSWORD', 'admin123'))
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

# 启动服务器
echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 myproject.asgi:application