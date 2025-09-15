import { defineStore } from 'pinia'
import { authAPI, postAPI, commentAPI, likeAPI,notificationAPI } from '../api'

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    posts: [],
    currentPost: null,
    notifications: [],
    unreadNotificationCount: 0
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
  }
})