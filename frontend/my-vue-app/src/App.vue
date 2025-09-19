<script setup>
import { ref, watch, onMounted } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useMainStore } from './store'
import { authAPI } from './api'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem, ElIcon, ElAvatar, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { HomeFilled, UserFilled, Edit, SwitchButton, Bell, ChatDotRound } from '@element-plus/icons-vue'
import NotificationBell from './components/NotificationBell.vue'
import websocket from './services/websocket'
const store = useMainStore()
const router = useRouter()
const route = useRoute()

const activeIndex = ref('/')


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
  switch(key) {
    case '/':
      router.push('/')
      break
    case '/forum':
      router.push('/forum')
      break
    case '/messages':
      router.push('/messages')
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
        <!-- 左侧导航 -->
        <div class="nav-left">
          <div class="nav-brand">
            <h2>Social Network</h2>
          </div>
          
          <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            @select="handleSelect"
            class="nav-menu"
          >
            <el-menu-item index="/"> 
              <el-icon><HomeFilled /></el-icon>
              <span class="menu-text">首页</span>
            </el-menu-item>
            
            <el-menu-item index="/forum">
              <el-icon><Edit /></el-icon>
              <span class="menu-text">论坛</span>
            </el-menu-item>
            
            <el-menu-item index="/profile">
              <el-icon><UserFilled /></el-icon>
              <span class="menu-text">个人中心</span>
            </el-menu-item>
          </el-menu>
        </div>
        
        <!-- 右侧用户操作 -->
        <div class="nav-right">
          <template v-if="store.user">
            <!-- 消息通知 -->
            <NotificationBell />
            
            <!-- 私信入口 -->
            <div class="messages-icon" @click="() => router.push('/messages')">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            
            <!-- 用户菜单 -->
            <el-dropdown class="user-dropdown">
              <div class="user-info">
                <el-avatar :size="30" :src="store.user.avatar || ''" class="user-avatar">
                  {{ store.user.username?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <span class="username">{{ store.user.username }}</span>
              </div>
              
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="() => router.push(`/profile/${store.user.id}`)">
                    <el-icon><UserFilled /></el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item @click="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          
          <template v-else>
            <el-menu
              mode="horizontal"
              @select="handleSelect"
              class="auth-menu"
            >
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
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.header {
  padding: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
  background-color: #4CAF50;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 10px;
}

.nav-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  flex: 1;
}

.nav-brand {
  color: white;
  padding: 0 1rem;
  white-space: nowrap;
}

.nav-brand h2 {
  margin: 0;
  font-size: 1.2rem;
}

.nav-menu {
  display: flex;
  align-items: center;
  background-color: transparent !important;
  border: none !important;
  flex: 1;
}

.nav-menu :deep(.el-menu-item) {
  display: flex;
  align-items: center;
  height: 50px;
  line-height: 50px;
  margin: 0 5px;
  border-bottom: none !important;
  color: white !important;
  padding: 0 15px !important;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: #ffd04b !important;
}

.nav-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.nav-right {
  display: flex;
  align-items: center;
  height: 100%;
  flex-shrink: 0;
}

.auth-menu {
  display: flex;
  align-items: center;
  background-color: transparent !important;
  border: none !important;
}

.auth-menu :deep(.el-menu-item) {
  display: flex;
  align-items: center;
  height: 50px;
  line-height: 50px;
  border-bottom: none !important;
  padding: 0 10px;
  color: white !important;
}

.auth-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.messages-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 15px;
  cursor: pointer;
  color: white;
  font-size: 18px;
  transition: all 0.3s ease;
  position: relative;
  border-radius: 4px;
}

.messages-icon:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.messages-icon:active {
  transform: translateY(0);
  background-color: rgba(255, 255, 255, 0.1);
}

.user-dropdown {
  height: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 1rem;
  cursor: pointer;
  color: white;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.user-info:active {
  transform: translateY(0);
  background-color: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  background-color: #c0c4cc;
  transition: all 0.3s ease;
}

.user-info:hover .user-avatar {
  transform: scale(1.05);
}

.username {
  margin-left: 8px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.user-info:hover .username {
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.menu-text {
  margin-left: 5px;
}

@media (max-width: 768px) {
  .nav-brand h2 {
    font-size: 1rem;
  }
  
  .username {
    display: none;
  }
  
  .menu-text {
    display: inline !important;
  }
  
  .nav-menu :deep(.el-menu-item .el-icon) {
    margin-right: 0;
  }
  
  .nav-menu :deep(.el-menu-item) {
    padding: 0 10px !important;
  }
  
  .nav-menu :deep(.el-menu-item span) {
    display: none;
  }
  
  .nav-menu :deep(.el-menu-item .menu-text) {
    display: inline !important;
  }
  
  .messages-icon {
    padding: 0 10px;
  }
}
</style>