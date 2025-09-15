API 文档
后端 API 使用 Django REST Framework 开发，可以通过以下 URL 访问 API 文档：

/api/docs/ - 自动生成的 API 文档
主要 API 端点：

/api/register/ - 用户注册
/api/login/ - 用户登录
/api/posts/ - 帖子列表和创建
/api/posts/<id>/ - 特定帖子详情
/api/posts/<id>/comments/ - 帖子评论
/api/profiles/<id>/ - 用户资料
/api/profiles/<id>/follow/ - 关注用户
前端路由
/ - 首页
/login - 登录页面
/register - 注册页面
/profile - 用户个人资料
/profile/:id - 其他用户资料
/edit-profile - 编辑个人资料
/forum - 论坛页面
/post/:id - 帖子详情页面
/following - 关注用户的信息流
数据库设计
用户表 (accounts)
用户名
邮箱
密码
个人简介
头像
帖子表 (posts)
标题
内容
作者 (外键到用户表)
创建时间
更新时间
评论表 (interactions)
内容
作者 (外键到用户表)
帖子 (外键到帖子表)
创建时间
点赞表 (interactions)
用户 (外键到用户表)
帖子 (外键到帖子表)
创建时间
关注表 (interactions)
关注者 (外键到用户表)
被关注者 (外键到用户表)
创建时间
开发指南
后端开发
所有 API 接口都在/api/路径下
使用 Django REST Framework 序列化器处理数据
使用基于类的视图(CBV)组织代码
数据库模型定义在各应用的 models.py 文件中
前端开发
使用 Vue 3 Composition API
使用 Vue Router 处理路由
使用 Vuex 进行状态管理
组件位于 src/components/目录
页面视图位于 src/views/目录
API 调用封装在 src/api/目录
贡献指南
Fork 项目
创建功能分支 (git checkout -b feature/AmazingFeature)
提交更改 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
开启 Pull Request
