import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ForumView from '../views/ForumView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import PostView from '../views/PostView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/forum',
    name: 'forum',
    component: ForumView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/profile/:id?',
    name: 'profile',
    component: ProfileView
  },
  {
    path: '/post/:id',
    name: 'post',
    component: PostView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  // 允许访问的公开页面
  const publicPages = ['/login', '/register', '/']
  const authRequired = !publicPages.includes(to.path)

  // 如果访问受保护的页面但未登录，则重定向到登录页
  if (authRequired && !token) {
    return next('/login')
  }

  // 如果已登录并尝试访问登录页，重定向到首页
  if (token && to.path === '/login') {
    return next('/')
  }

  next()
})

export default router