import { defineStore } from "pinia";
import {
  authAPI,
  postAPI,
  commentAPI,
  likeAPI,
  notificationAPI,
  messageAPI,
} from "../api";
import websocket from "../services/websocket";

export const useMainStore = defineStore("main", {
  state: () => ({
    user: null,
    posts: [],
    currentPost: null,
    notifications: [],
    unreadNotificationCount: 0,
    conversations: [],
    currentConversation: null,
    groupChats: [],
  }),

  actions: {
    setUser(user) {
      this.user = user;
    },

    setPosts(posts) {
      this.posts = posts;
    },

    addPost(post) {
      this.posts.unshift(post);
    },

    setCurrentPost(post) {
      this.currentPost = post;
    },

    addCommentToPost(postId, comment) {
      const post = this.posts.find((p) => p.id === postId);
      if (post) {
        if (!post.comments) {
          post.comments = [];
        }
        post.comments.push(comment);
      }
    },

    toggleLike(postId, isLiked) {
      const post = this.posts.find((p) => p.id === postId);
      if (post) {
        // 更新点赞状态和计数
        post.is_liked = isLiked;
        // 重新计算点赞数（如果需要的话）
        if (isLiked) {
          post.likes_count = (post.likes_count || 0) + 1;
        } else {
          post.likes_count = Math.max(0, (post.likes_count || 0) - 1);
        }
      }
    },

    async fetchNotifications() {
      try {
        const response = await notificationAPI.getNotifications();
        this.notifications = response.data;
      } catch (error) {
        console.error("Error fetching notifications:", error);
      }
    },

    async markNotificationAsRead(notificationId) {
      try {
        await notificationAPI.markAsRead(notificationId);
        const notification = this.notifications.find(
          (n) => n.id === notificationId
        );
        if (notification) {
          notification.is_read = true;
        }
        this.unreadNotificationCount = Math.max(
          0,
          this.unreadNotificationCount - 1
        );
      } catch (error) {
        console.error("Error marking notification as read:", error);
      }
    },

    async markAllNotificationsAsRead() {
      try {
        await notificationAPI.markAllAsRead();
        this.notifications.forEach((n) => {
          n.is_read = true;
        });
        this.unreadNotificationCount = 0;
      } catch (error) {
        console.error("Error marking all notifications as read:", error);
      }
    },

    async fetchUnreadNotificationCount() {
      try {
        const response = await notificationAPI.getUnreadCount();
        this.unreadNotificationCount = response.data.count;
      } catch (error) {
        console.error("Error fetching unread notification count:", error);
      }
    },

    async fetchConversations() {
      try {
        const response = await messageAPI.getConversations();
        // 合并私聊和群聊数据
        this.conversations = [
          ...(response.data.private_chats || []),
          ...(response.data.group_chats || []),
        ];

        // 更新全局未读计数
        await this.fetchUnreadNotificationCount();
      } catch (error) {
        console.error("Error fetching conversations:", error);
      }
    },

    async fetchConversation(userId, page = 1, pageSize = 20) {
      try {
        const response = await messageAPI.getMessages(userId, page, pageSize);

        if (page === 1) {
          // 第一页，替换所有消息
          this.currentConversation = {
            userId,
            messages: response.data.results || response.data || [],
            pagination: {
              count: response.data.count || 0,
              page: response.data.page || 1,
              page_size: response.data.page_size || 20,
              has_next: response.data.has_next || false,
              has_previous: response.data.has_previous || false,
            },
          };
        } else {
          // 后续页面，追加消息到现有列表
          if (
            this.currentConversation &&
            this.currentConversation.userId === userId
          ) {
            this.currentConversation.messages = [
              ...(response.data.results || response.data || []),
              ...this.currentConversation.messages,
            ];

            // 更新分页信息
            this.currentConversation.pagination = {
              count: response.data.count || 0,
              page: response.data.page || page,
              page_size: response.data.page_size || pageSize,
              has_next: response.data.has_next || false,
              has_previous: response.data.has_previous || page > 1,
            };
          }
        }

        // 标记所有未读消息为已读（仅对第一页执行）
        if (
          page === 1 &&
          Array.isArray(response.data.results || response.data)
        ) {
          // 先过滤出有效的未读消息
          const unreadMessages = (
            response.data.results || response.data
          ).filter((msg) => {
            // 确保msg对象存在且具有必要的属性
            return (
              msg &&
              typeof msg === "object" &&
              msg.is_read === false &&
              msg.recipient &&
              typeof msg.recipient === "object" &&
              msg.recipient.id &&
              this.user &&
              this.user.id &&
              msg.recipient.id === this.user.id &&
              msg.id
            );
          });

          // 逐个标记未读消息为已读
          for (const message of unreadMessages) {
            try {
              await messageAPI.markAsRead(message.id);
              // 也通过WebSocket通知发送者
              websocket.markAsRead(message.id);
            } catch (error) {
              console.error("Error marking message as read:", error);
            }
          }
        }

        // 更新全局未读计数
        await this.fetchUnreadNotificationCount();
      } catch (error) {
        console.error("获取会话失败:", error);
        throw error;
      }
    },

    async loadMoreMessages(userId) {
      if (
        this.currentConversation &&
        this.currentConversation.userId === userId &&
        this.currentConversation.pagination &&
        this.currentConversation.pagination.has_next
      ) {
        const nextPage = this.currentConversation.pagination.page + 1;
        await this.fetchConversation(userId, nextPage);
      }
    },

    // 添加获取群聊列表的action
    async fetchGroupChats() {
      try {
        const response = await messageAPI.getConversations();
        this.groupChats = response.data.group_chats || [];
      } catch (error) {
        console.error("Error fetching group chats:", error);
      }
    },

    async sendMessage(userId, messageContent) {
      try {
        // 通过WebSocket发送消息
        return new Promise((resolve, reject) => {
          // 设置超时
          const timeout = setTimeout(() => {
            reject(new Error("Message send timeout"));
          }, 10000);

          // 监听WebSocket响应
          const messageHandler = (data) => {
            if (data.type === "message") {
              clearTimeout(timeout);
              websocket.off("message", messageHandler);

              const newMessage = {
                ...data.message,
                sender: data.message.sender || this.user,
                recipient: data.message.recipient || { id: userId },
                timestamp: data.message.timestamp || new Date().toISOString(),
                is_read: data.message.is_read || false,
              };

              if (
                !this.currentConversation ||
                this.currentConversation.userId !== userId
              ) {
                this.currentConversation = {
                  userId,
                  messages: [],
                };
              }

              // 检查消息是否已经存在于列表中
              const existingMessageIndex =
                this.currentConversation.messages.findIndex(
                  (msg) => msg.id === newMessage.id
                );

              if (existingMessageIndex !== -1) {
                this.currentConversation.messages[existingMessageIndex] =
                  newMessage;
              } else {
                this.currentConversation.messages.push(newMessage);
              }

              resolve(newMessage);
            }
          };

          websocket.on("message", messageHandler);

          // 发送消息
          websocket.sendMessage(userId, messageContent);
        });
      } catch (error) {
        console.error("Failed to send message via WebSocket:", error);
        // 如果WebSocket失败，回退到HTTP API
        try {
          const messageData = {
            recipient: userId,
            content: messageContent,
          };
          const response = await messageAPI.sendMessage(messageData);

          if (
            !this.currentConversation ||
            this.currentConversation.userId !== userId
          ) {
            this.currentConversation = {
              userId,
              messages: [],
            };
          }

          if (response.data) {
            const newMessage = {
              ...response.data,
              sender: response.data.sender || this.user,
              recipient: response.data.recipient || { id: userId },
              timestamp: response.data.timestamp || new Date().toISOString(),
              is_read: response.data.is_read || false,
            };

            const existingMessageIndex =
              this.currentConversation.messages.findIndex(
                (msg) => msg.id === newMessage.id
              );

            if (existingMessageIndex !== -1) {
              this.currentConversation.messages[existingMessageIndex] =
                newMessage;
            } else {
              this.currentConversation.messages.push(newMessage);
            }

            return newMessage;
          }
        } catch (httpError) {
          console.error("Failed to send message via HTTP:", httpError);
          throw httpError;
        }
      }
    },

    // 初始化WebSocket连接
    initWebSocket() {
      if (this.user) {
        websocket.connect();

        // 监听WebSocket消息
        websocket.on("message", (data) => {
          if (data.type === "message") {
            // 处理接收到的新消息
            this.handleIncomingMessage(data.message);
          }
        });
      }
    },

    // 处理接收到的新消息
    handleIncomingMessage(message) {
      // 更新当前对话（如果正在查看该对话）
      if (
        this.currentConversation &&
        (message.sender.id === this.currentConversation.userId ||
          message.recipient.id === this.currentConversation.userId)
      ) {
        const existingMessageIndex =
          this.currentConversation.messages.findIndex(
            (msg) => msg.id === message.id
          );

        if (existingMessageIndex !== -1) {
          this.currentConversation.messages[existingMessageIndex] = message;
        } else {
          this.currentConversation.messages.push(message);
        }
      }

      // 更新对话列表
      const conversationIndex = this.conversations.findIndex(
        (conv) => conv.user.id === message.sender.id
      );

      if (conversationIndex !== -1) {
        this.conversations[conversationIndex] = {
          ...this.conversations[conversationIndex],
          last_message: {
            content: message.content,
            timestamp: message.timestamp,
            is_read: message.is_read,
          },
          unread_count: this.conversations[conversationIndex].unread_count + 1,
        };
      } else {
        // 添加新对话
        this.conversations.unshift({
          user: message.sender,
          last_message: {
            content: message.content,
            timestamp: message.timestamp,
            is_read: false,
          },
          unread_count: 1,
        });
      }

      // 更新未读计数
      this.unreadNotificationCount += 1;
    },
  },
});
