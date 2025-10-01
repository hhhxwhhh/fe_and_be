import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
});

// 添加请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 如果是FormData，让浏览器自动设置Content-Type（包含boundary）
    if (config.data instanceof FormData) {
      delete config.headers["Content-Type"];
    } else if (!config.headers["Content-Type"]) {
      // 只对非FormData请求设置默认Content-Type
      config.headers["Content-Type"] = "application/json";
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器处理认证问题
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 检查是否是401未授权错误
    if (error.response && error.response.status === 401) {
      // 清除本地存储的令牌
      localStorage.removeItem("token");
      // 可以在这里添加重定向到登录页面的逻辑，或者让路由守卫处理
      console.log("认证已过期，请重新登录");
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  login: (credentials) => api.post("/auth/login/", credentials),
  register: (userData) => api.post("/auth/register/", userData),
  profile: () => api.get("/auth/profile/"),
  userProfile: (userId) => api.get(`/auth/${userId}/`),
  updateProfile: (userData) => api.put("/auth/profile/", userData),
  getUsers: () => api.get("/auth/users/"),
};

// 帖子相关API
export const postAPI = {
  getPosts: () => api.get("/posts/"),
  getAllPosts: () => api.get("/posts/?all=true"),
  getPost: (id) => api.get(`/posts/${id}/`),
  createPost: (postData) => api.post("/posts/", postData),
  updatePost: (id, postData) => api.put(`/posts/${id}/`, postData),
  deletePost: (id) => api.delete(`/posts/${id}/`),
  getUserPosts: (userId) => api.get(`/posts/user/${userId}/`),
};

// 评论相关API
export const commentAPI = {
  getComments: (postId) => api.get(`/posts/${postId}/comments/`),
  createComment: (postId, commentData) =>
    api.post(`/posts/${postId}/comments/`, commentData),
  deleteComment: (commentId) => api.delete(`/posts/comments/${commentId}/`),
};

// 点赞相关API
export const likeAPI = {
  likePost: (postId) => api.post(`/posts/${postId}/like/`),
  unlikePost: (postId) => api.delete(`/posts/${postId}/like/`),
};

// 通知相关API
export const notificationAPI = {
  getNotifications: () => api.get("/interactions/notifications/"),
  markAsRead: (notificationId) =>
    api.post(`/interactions/notifications/${notificationId}/read/`),
  markAllAsRead: () => api.post("/interactions/notifications/read-all/"),
  getUnreadCount: () => api.get("/interactions/notifications/unread-count/"),
};

// 搜索相关API
export const searchAPI = {
  search: (query, type = "all") =>
    api.get(`/posts/search/`, {
      params: { q: query, type },
    }),
};

// 消息相关API
export const messageAPI = {
  getConversations: () => api.get("/messages/conversations/"),
  getMessages: (userId, page = 1, pageSize = 20) =>
    api.get(`/messages/conversations/${userId}/`, {
      params: { page, page_size: pageSize },
    }),
  sendMessage: (messageData) => api.post("/messages/messages/", messageData),
  updateMessage: (messageId, messageData) =>
    api.put(`/messages/messages/${messageId}/`, messageData),
  deleteMessage: (messageId) => api.delete(`/messages/messages/${messageId}/`),
  revokeMessage: (messageId) =>
    api.patch(`/messages/messages/${messageId}/revoke/`),
  markAsRead: (messageId) => api.patch(`/messages/messages/${messageId}/read/`),

  // 群聊相关API
  getGroupChat: (groupId) => api.get(`/messages/group-chats/${groupId}/`),
  createGroupChat: (groupData) => {
    return api.post("/messages/group-chats/", groupData);
  },
  getGroupMessages: (groupId) =>
    api.get(`/messages/group-messages/`, {
      params: { group_id: groupId },
    }),
  addGroupMember: (groupId, userId) =>
    api.post(`/messages/group-chats/${groupId}/add_member/`, {
      user_id: userId,
    }),
  removeGroupMember: (groupId, userId) =>
    api.post(`/messages/group-chats/${groupId}/remove_member/`, {
      user_id: userId,
    }),
};
export { api };
