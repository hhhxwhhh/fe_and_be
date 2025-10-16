# 社交平台项目

这是一个社交平台项目，包含前后端代码以及Docker部署配置。

## 项目结构

### 后端 (backend/)
后端基于Django框架构建，包含以下模块：
- accounts/: 用户账户模块
- posts/: 帖子模块
- interactions/: 互动模块（点赞、关注等）
- messaging/: 消息模块
- ai/: AI集成模块
- myproject/: Django项目配置

### 前端 (frontend/)
前端使用Vue.js框架开发：
- my-vue-app/: Vue应用程序
  - src/components/: Vue组件
  - src/views/: 页面视图
  - src/api/: API接口
  - src/store/: 状态管理
  - src/router/: 路由配置

### 部署配置
- docker-compose.yml: Docker编排文件，用于容器化部署整个应用