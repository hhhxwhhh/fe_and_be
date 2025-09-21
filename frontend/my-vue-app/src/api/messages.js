import axios from 'axios'
import websocket from '../services/websocket'
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
  return api.get(`/messages/users/${userId}/messages/`)
}

// 发送消息
export const sendMessage = (messageData) => {
  return api.post('/messages/messages/', messageData)
}

// 更新消息
export const updateMessage = (messageId, data) => {
  return api.put(`/messages/messages/${messageId}/`, data)
}

// 删除消息
export const deleteMessage = (messageId) => {
  return api.delete(`/messages/messages/${messageId}/`)
}

// 标记消息为已读
export const markAsRead = (messageId) => {
  return api.patch(`/messages/messages/${messageId}/read/`)
}

// 支持WebSocket回退
export const sendMessageWithFallback = async (messageData) => {
  // 首先尝试通过WebSocket发送
  if (websocket.isConnected) {
    try {
      return await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket timeout'));
        }, 5000);
        
        websocket.sendMessage(messageData.recipient, messageData.content);
        
        // 这里需要根据实际的后端响应来处理
        setTimeout(() => {
          clearTimeout(timeout);
          resolve({ data: { success: true } });
        }, 100);
      });
    } catch (error) {
      console.warn('WebSocket发送失败，回退到HTTP:', error);
    }
  }
  
  // 如果WebSocket不可用，使用HTTP API
  return api.post('/messages/messages/', messageData);
};

// 默认导出整个API对象
export default {
  getConversations,
  getMessages,
  sendMessage,
  updateMessage,
  deleteMessage,
  markAsRead
}