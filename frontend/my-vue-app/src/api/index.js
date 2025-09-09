import axios from 'axios'

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
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// 用户相关API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  profile: () => api.get('/auth/profile/'),  // 获取当前用户资料
  userProfile: (id) => api.get(`/auth/${id}/`),  // 获取指定用户资料
  userPosts: (id) => api.get(`/auth/${id}/posts/`),  // 获取用户帖子
  updateProfile: (data) => api.put('/auth/profile/', data),  // 更新当前用户资料
  followUser: (id) => api.post(`/auth/${id}/follow/`),
  unfollowUser: (id) => api.post(`/auth/${id}/unfollow/`)
}

// 帖子相关API
export const postAPI = {
  getPosts: () => api.get('/posts/'),
  createPost: (data) => api.post('/posts/', data),
  getPost: (id) => api.get(`/posts/${id}/`),
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