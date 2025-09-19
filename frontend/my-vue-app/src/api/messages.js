import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// 创建一个不带拦截器的新axios实例专门用于消息
const api = axios.create({
  baseURL: API_BASE_URL
})

// 添加请求拦截器
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

// 添加响应拦截器处理认证问题
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
    return Promise.reject(error)
  }
)

// 获取对话列表
export const getConversations = () => {
  return api.get('/messages/conversations/')
}

// 获取与特定用户的对话
export const getMessages = (userId) => {
  return api.get(`/messages/messages/${userId}/`)
}

// 发送消息
export const sendMessage = (messageData) => {
  return api.post('/messages/messages/', messageData)
}

// 标记消息为已读
export const markAsRead = (messageId) => {
  return api.patch(`/messages/messages/${messageId}/read/`)
}

// 默认导出整个API对象
export default {
  getConversations,
  getMessages,
  sendMessage,
  markAsRead
}