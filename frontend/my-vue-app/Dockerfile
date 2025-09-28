# 构建阶段
FROM node:22-alpine AS build-stage

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 使用npm install安装依赖 使用国内镜像源
RUN npm config set registry https://registry.npmmirror.com
RUN npm install --prefer-offline --no-audit --no-fund --legacy-peer-deps

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:alpine AS production-stage

# 复制构建产物到nginx目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]