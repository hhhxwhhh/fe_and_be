<script setup>
import { ref, watch, onMounted } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useMainStore } from './store'
import { authAPI } from './api'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem, ElIcon, ElAvatar } from 'element-plus'
import { HomeFilled, UserFilled, Edit, SwitchButton } from '@element-plus/icons-vue'

const store = useMainStore()
const router = useRouter()
const route = useRoute()

const activeIndex = ref('/')

// 监听路由变化，更新激活的菜单项
watch(() => route.path, (newPath) => {
  // 处理动态路由，例如 /profile/1 应该激活 /profile
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
      localStorage.removeItem('token')
    }
  }
})
</script>

<template>
  <el-container id="app">
    <el-header>
      <div class="header-container">
        <div class="nav-left">
          <div class="nav-brand">
            <h2>Social Network</h2>
          </div>
          
          <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            @select="handleSelect"
            background-color="#42b883"
            text-color="#fff"
            active-text-color="#ffd04b"
            class="nav-menu"
          >
            <el-menu-item index="/"> 
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            
            <el-menu-item index="/forum">
              <el-icon><Edit /></el-icon>
              <span>论坛</span>
            </el-menu-item>
            
            <el-menu-item index="/profile">
              <el-icon><UserFilled /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
            
          </el-menu>
        </div>
        
        <div class="nav-right">
          <template v-if="store.user">
            <div class="user-info" @click="handleSelect('/profile')">
              <el-avatar :size="30" :src="store.user.avatar || ''">
                {{ store.user.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ store.user.username }}</span>
            </div>
            <el-menu
              mode="horizontal"
              @select="handleSelect"
              background-color="#42b883"
              text-color="#fff"
              active-text-color="#ffd04b"
              class="user-menu"
            >
              <el-menu-item index="#" @click="logout">
                退出
              </el-menu-item>
            </el-menu>
          </template>
          
          <template v-else>
            <el-menu
              mode="horizontal"
              @select="handleSelect"
              background-color="#42b883"
              text-color="#fff"
              active-text-color="#ffd04b"
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

.el-header {
  padding: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #42b883;
  height: 50px;
}

.nav-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-brand {
  color: white;
  padding: 0 1rem;
}

.nav-brand h2 {
  margin: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  background-color: transparent !important;
  border: none !important;
}

.nav-menu :deep(.el-menu-item) {
  display: flex;
  align-items: center;
  height: 50px;
  line-height: 50px;
  margin: 0 5px;
  border-bottom: none !important;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: #ffd04b !important;
}

.nav-right {
  display: flex;
  align-items: center;
  height: 100%;
}

.user-menu,
.auth-menu {
  display: flex;
  align-items: center;
  background-color: transparent !important;
  border: none !important;
}

.user-menu :deep(.el-menu-item),
.auth-menu :deep(.el-menu-item) {
  display: flex;
  align-items: center;
  height: 50px;
  line-height: 50px;
  margin: 0 5px;
  border-bottom: none !important;
}

.user-info {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 1rem;
  cursor: pointer;
  color: white;
  height: 50px;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.username {
  margin-left: 8px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .nav-brand h2 {
    font-size: 1.2rem;
  }
  
  .username {
    display: none;
  }
}
</style>