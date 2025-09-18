import axios from 'axios'
import { getAuthToken } from './index'

const API_BASE_URL = '/api/messages'

const api = axios.create({
  baseURL: API_BASE_URL
})

// 添加请求拦截器
api.interceptors.request.use(
  config => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 获取对话列表
export const getConversations = () => {
  return api.get('/conversations/')
}

// 获取与特定用户的对话
export const getMessages = (userId) => {
  return api.get(`/messages/${userId}/`)
}

// 发送消息
export const sendMessage = (messageData) => {
  return api.post('/messages/', messageData)
}

// 标记消息为已读
export const markAsRead = (messageId) => {
  return api.patch(`/messages/${messageId}/read/`)
}

export default {
  getConversations,
  getMessages,
  sendMessage,
  markAsRead
}