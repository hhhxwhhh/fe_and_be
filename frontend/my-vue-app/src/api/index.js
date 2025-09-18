import axios from 'axios'
import messageAPI from './messages'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 如果是FormData，让浏览器自动设置Content-Type（包含boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    } else if (!config.headers['Content-Type']) {
      // 只对非FormData请求设置默认Content-Type
      config.headers['Content-Type'] = 'application/json';
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    // 检查是否是401未授权错误
    if (error.response && error.response.status === 401) {
      // 清除本地存储的令牌
      localStorage.removeItem('token')
      // 可以在这里添加重定向到登录页面的逻辑，或者让路由守卫处理
      console.log('认证已过期，请重新登录')
    }
    // 不再自动重定向到登录页面，让路由守卫处理
    return Promise.reject(error)
  }
)

export {
  messageAPI
}

export default api

// 用户相关API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  profile: () => api.get('/auth/profile/'),  // 获取当前用户资料
  userProfile: (id) => api.get(`/auth/${id}/`),  // 获取指定用户资料
  userPosts: (id) => api.get(`/posts/user/${id}/`),  // 获取用户帖子
  updateProfile: (data) => api.put('/auth/profile/', data,{
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),  // 更新当前用户资料
  followUser: (id) => api.post(`/auth/${id}/follow/`),
  unfollowUser: (id) => api.post(`/auth/${id}/unfollow/`)
}

// 帖子相关API
export const postAPI = {
  getPosts: () => api.get('/posts/'),//获取关注的用户以及自己的帖子
  getAllPosts: () => api.get('/posts/?all=true'),//获取所有人发的帖子
  createPost: (data) => api.post('/posts/', data),
  getPost: (id) => api.get(`/posts/${id}/`),
  getUserPosts: (userId) => api.get(`/posts/user/${userId}/`), // 获取特定用户的帖子
  updatePost: (id, data) => api.put(`/posts/${id}/`, data),
  deletePost: (id) => api.delete(`/posts/${id}/`)
}

// 评论相关API
export const commentAPI = {
  createComment: (postId, data) => api.post(`/posts/${postId}/comments/`, data),
  deleteComment: (postId, commentId) => api.delete(`/posts/${postId}/comments/${commentId}/`)
}

// 点赞相关API
export const likeAPI = {
  likePost: (postId) => api.post(`/posts/${postId}/like/`),
  unlikePost: (postId) => api.delete(`/posts/${postId}/like/`)
}

export const notificationAPI = {
  getNotifications: () => api.get('/interactions/notifications/'),
  markAsRead: (id) => api.post(`/interactions/notifications/${id}/read/`),
  markAllAsRead: () => api.post('/interactions/notifications/read-all/'),
  getUnreadCount: () => api.get('/interactions/notifications/unread-count/')
}