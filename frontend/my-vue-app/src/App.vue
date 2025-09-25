<script setup>
import { ref, watch, onMounted } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useMainStore } from './store'
import { authAPI } from './api'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem, ElIcon, ElAvatar, ElDropdown, ElDropdownMenu, ElDropdownItem, ElInput } from 'element-plus'
import { HomeFilled, UserFilled, Edit, SwitchButton, Bell, ChatDotRound, Phone, User, Comment, Search } from '@element-plus/icons-vue'
import NotificationBell from './components/NotificationBell.vue'
import websocket from './services/websocket'
const store = useMainStore()
const router = useRouter()
const route = useRoute()

const activeIndex = ref('/')
const searchQuery = ref('')


watch(() => store.user, (newUser) => {
  if (newUser) {
    store.initWebSocket()
  } else {

    websocket.disconnect()
  }
})




// 监听路由变化，更新激活的菜单项
watch(() => route.path, (newPath) => {
  if (newPath.startsWith('/profile/')) {
    activeIndex.value = '/profile'
  } else {
    activeIndex.value = newPath
  }
}, { immediate: true })

const handleSelect = (key) => {
  activeIndex.value = key
  // 根据菜单项跳转到相应页面
  switch (key) {
    case '/':
      router.push('/')
      break
    case '/forum':
      router.push('/forum')
      break
    case '/messages':
      router.push('/messages')
      break
    case '/group-chats':
      router.push('/group-chats')
      break
    case '/contacts':
      router.push('/contacts')
      break
    case '/login':
      router.push('/login')
      break
    case '/register':
      router.push('/register')
      break
    case '/profile':
      if (store.user) {
        router.push(`/profile/${store.user.id}`)
      } else {
        router.push('/login')
      }
      break
  }
}

const logout = () => {
  localStorage.removeItem('token')
  store.setUser(null)
  router.push('/login')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value.trim())}`)
  }
}

// 页面加载时检查用户状态
onMounted(async () => {
  // 如果有token但store中没有用户信息，尝试获取用户信息
  const token = localStorage.getItem('token')
  if (token && !store.user) {
    try {
      const response = await authAPI.profile()
      store.setUser(response.data)
    } catch (error) {
      // 如果获取用户信息失败，清除无效token
      console.error('获取用户信息失败，清除无效token')
      localStorage.removeItem('token')
      store.setUser(null)
    }
  }

  // 如果用户已登录，获取未读通知数
  if (store.user) {
    store.fetchUnreadNotificationCount()
  }
})
</script>

<template>
  <el-container id="app">
    <el-header class="header">
      <div class="header-container">
        <div class="nav-left">
          <div class="logo-container">
            <img src="../public/xw_chat.svg" class="logo"></img>
            <div class="nav-brand">
              <h2>Social Network</h2>
            </div>
          </div>

          <el-menu :default-active="activeIndex" mode="horizontal" @select="handleSelect" class="nav-menu"
            :ellipsis="false">
            <el-menu-item index="/">
              <el-icon class="nav-icon">
                <HomeFilled />
              </el-icon>
              <span class="menu-text">首页</span>
            </el-menu-item>

            <el-menu-item index="/forum">
              <el-icon class="nav-icon">
                <Edit />
              </el-icon>
              <span class="menu-text">论坛</span>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="nav-center" v-if="store.user">
          <div class="search-container">
            <el-input v-model="searchQuery" placeholder="搜索用户或帖子..." class="nav-search-input"
              @keyup.enter="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
          </div>
        </div>
        <div class="nav-right">
          <template v-if="store.user">
            <!-- 消息 -->
            <div class="nav-icon-button" @click="() => router.push('/messages')">
              <div class="icon-wrapper">
                <el-icon>
                  <ChatDotRound />
                </el-icon>
              </div>
              <span class="icon-text">消息</span>
            </div>

            <!-- 群聊 -->
            <div class="nav-icon-button" @click="() => router.push('/group-chats')">
              <div class="icon-wrapper">
                <el-icon>
                  <Comment />
                </el-icon>
              </div>
              <span class="icon-text">群聊</span>
            </div>

            <!-- 联系人 -->
            <div class="nav-icon-button" @click="() => router.push('/contacts')">
              <div class="icon-wrapper">
                <el-icon>
                  <Phone />
                </el-icon>
              </div>
              <span class="icon-text">联系人</span>
            </div>

            <!-- AI助手 -->
            <div class="nav-icon-button" @click="() => router.push('/ai-chat')">
              <div class="icon-wrapper">
                <el-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                    viewBox="0 0 16 16">
                    <path
                      d="M8 0c4.418 0 8 3.358 8 7.5s-3.582 7.5-8 7.5S0 11.642 0 7.5 3.582 0 8 0zm0 1C4.136 1 1 4.136 1 8s3.136 7 7 7 7-3.136 7-7-3.136-7-7-7z" />
                    <path
                      d="M8 4a.5.5 0 0 1 .5.5v1.793l.975-.975a.5.5 0 0 1 .707.707l-1.5 1.5a.5.5 0 0 1-.707 0l-1.5-1.5a.5.5 0 1 1 .707-.707L7.5 6.293V4.5A.5.5 0 0 1 8 4zm-3 5a.5.5 0 0 1 .5.5v.5h5v-.5a.5.5 0 0 1 1 0v.5a1.5 1.5 0 0 1-1.5 1.5h-5A1.5 1.5 0 0 1 4 11v-.5a.5.5 0 0 1 .5-.5z" />
                  </svg>
                </el-icon>
              </div>
              <span class="icon-text">AI助手</span>
            </div>

            <!-- 通知 -->
            <NotificationBell />

            <!-- 用户菜单 -->
            <el-dropdown class="user-dropdown">
              <div class="user-info">
                <el-avatar :size="32" :src="store.user.avatar || ''" class="user-avatar">
                  {{ store.user.username?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <span class="username">{{ store.user.username }}</span>
              </div>

              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="() => router.push(`/profile/${store.user.id}`)">
                    <el-icon>
                      <UserFilled />
                    </el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item @click="logout">
                    <el-icon>
                      <SwitchButton />
                    </el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <el-menu mode="horizontal" @select="handleSelect" class="auth-menu" :ellipsis="false">
              <el-menu-item index="/login">
                登录
              </el-menu-item>
              <el-menu-item index="/register">
                注册
              </el-menu-item>
            </el-menu>
          </template>
        </div>
      </div>
    </el-header>

    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
#app {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.header {
  padding: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 64px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 30px;
  flex-shrink: 0;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  height: 36px;
}

.nav-brand h2 {
  margin: 0;
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
}

.nav-menu {
  border: none !important;
  background: transparent !important;
}

.nav-menu :deep(.el-menu-item) {
  height: 64px;
  line-height: 64px;
  border: none !important;
  display: flex;
  align-items: center;
  padding: 0 20px !important;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
  border-radius: 8px;
  margin: 0 5px;
  transition: all 0.3s ease;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

.nav-icon {
  font-size: 16px;
  margin-right: 8px;
  width: 16px;
  height: 16px;
}

.nav-center {
  flex: 1;
  max-width: 400px;
  margin: 0 20px;
}

.nav-search-input {
  border-radius: 20px;
}

.nav-search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  box-shadow: none;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.nav-search-input :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.25);
}

.nav-search-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.3);
}

.nav-search-input :deep(.el-input__inner) {
  color: white;
  caret-color: white;
}

.nav-search-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

.nav-search-input :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.7);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
}

.nav-icon-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-icon-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
  border-radius: 20px;
}

.nav-icon-button:hover {
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-icon-button:hover::before {
  opacity: 1;
}

.nav-icon-button:active {
  transform: translateY(0);
  transition: all 0.1s ease;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.nav-icon-button:hover .icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.button-icon {
  font-size: 18px;
  transition: all 0.3s ease;
}

.nav-icon-button:hover .button-icon {
  transform: scale(1.2);
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  background: linear-gradient(135deg, #42b883, #3498db);
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.user-info:hover .user-avatar {
  transform: scale(1.05);
}

.username {
  font-weight: 500;
  color: white;
  font-size: 14px;
}

.auth-menu {
  border: none !important;
  background: transparent !important;
}

.auth-menu :deep(.el-menu-item) {
  height: 64px;
  line-height: 64px;
  border: none !important;
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
  padding: 0 15px !important;
  border-radius: 8px;
  margin: 0 5px;
  transition: all 0.3s ease;
}

.auth-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 15px;
  }

  .nav-brand h2 {
    font-size: 1.1rem;
  }

  .nav-menu :deep(.el-menu-item) {
    padding: 0 12px !important;
    font-size: 14px;
  }

  .nav-icon {
    margin-right: 4px;
  }

  .nav-icon-button .icon-text {
    display: none;
  }

  .nav-icon-button {
    padding: 6px 8px;
  }

  .icon-wrapper {
    width: 28px;
    height: 28px;
  }

  .username {
    display: none;
  }

  .user-info {
    gap: 5px;
  }

  .nav-center {
    max-width: 200px;
    margin: 0 10px;
  }
}
</style>