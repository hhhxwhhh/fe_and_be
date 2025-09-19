import { defineStore } from 'pinia'
import { authAPI, postAPI, commentAPI, likeAPI, notificationAPI, messageAPI } from '../api'

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    posts: [],
    currentPost: null,
    notifications: [],
    unreadNotificationCount: 0,
    conversations: [],
    currentConversation: null
  }),
  
  actions: {
    setUser(user) {
      this.user = user
    },
    
    setPosts(posts) {
      this.posts = posts
    },
    
    addPost(post) {
      this.posts.unshift(post)
    },
    
    setCurrentPost(post) {
      this.currentPost = post
    },
    
    addCommentToPost(postId, comment) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        if (!post.comments) {
          post.comments = []
        }
        post.comments.push(comment)
      }
    },
    
    toggleLike(postId) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        // 更新点赞状态和计数
        post.is_liked = !post.is_liked
        post.likes_count = post.is_liked ? (post.likes_count || 0) + 1 : Math.max(0, (post.likes_count || 0) - 1)
      }
    },
    async fetchNotifications() {
      try {
        const response = await notificationAPI.getNotifications()
        this.notifications = response.data;
      }catch(error) {
        console.error('Error fetching notifications:', error)
      }
    },

    async markNotificationAsRead(notificationId){
      try {
        await notificationAPI.markAsRead(notificationId);
        const notification=this.notifications.find(n => n.id === notificationId)
        if(notification){
          notification.is_read=true
        }
        this.unreadNotificationCount=Math.max(0, this.unreadNotificationCount - 1);
      }catch (error) {
        console.error('Error marking notification as read:', error);
      }
    },
  

    async markAllNotificationsAsRead() {
      try {
        await notificationAPI.markAllAsRead();
        this.notifications.forEach(n=>{
          n.is_read=true
        });
        this.unreadNotificationCount=0;
      }catch (error) {
        console.error('Error marking all notifications as read:', error);
      }
    },

    async fetchUnreadNotificationCount() { 
      try{
        const response = await notificationAPI.getUnreadCount();
        this.unreadNotificationCount = response.data.count;
      }catch(error) {
        console.error('Error fetching unread notification count:', error);
      }
    },

    async fetchConversations() {
      try {
        const response = await messageAPI.getConversations()
        this.conversations = response.data
        
        // 更新全局未读计数
        await this.fetchUnreadNotificationCount()
      } catch (error) {
        console.error('Error fetching conversations:', error)
      }
    },

        async fetchConversation(userId) {
      try {
        const response = await messageAPI.getMessages(userId);
        this.currentConversation = {
          userId,
          messages: response.data || []
        };
        
        // 标记所有未读消息为已读
        if (Array.isArray(response.data)) {
          // 先过滤出有效的未读消息
          const unreadMessages = response.data.filter(msg => {
            // 确保msg对象存在且具有必要的属性
            return msg && 
                   typeof msg === 'object' && 
                   msg.is_read === false && 
                   msg.recipient && 
                   typeof msg.recipient === 'object' && 
                   msg.recipient.id && 
                   this.user && 
                   this.user.id && 
                   msg.recipient.id === this.user.id && 
                   msg.id;
          });
          
          // 逐个标记未读消息为已读
          for (const message of unreadMessages) {
            try {
              await messageAPI.markAsRead(message.id);
            } catch (error) {
              console.error('Error marking message as read:', error);
            }
          }
        }
        
        // 更新全局未读计数
        await this.fetchUnreadNotificationCount();
      } catch (error) {
        console.error('Error fetching conversation:', error);
        // 如果获取对话失败，初始化一个空的对话
        this.currentConversation = {
          userId,
          messages: []
        };
      }
    },

    async sendMessage(userId, messageContent) {
      try {
        const messageData = {
          recipient: userId,
          content: messageContent
        };
        const response = await messageAPI.sendMessage(messageData); // 调用 API 发送消息
        if (!this.currentConversation || this.currentConversation.userId !== userId) {
          // 如果当前对话不存在或不是与该用户的对话，创建一个新的对话
          this.currentConversation = {
            userId,
            messages: []
          };
        }
        // 将新消息添加到当前对话的消息列表中
        if (response.data) {
          this.currentConversation.messages.push(response.data);
          return response.data;
        }
      } catch (error) {
        console.error('Failed to send message:', error);
        throw error;
      }
    },

  }

})