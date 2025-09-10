import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    posts: [],
    currentPost: null
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
    }
  }
})